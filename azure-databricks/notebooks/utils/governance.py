# Databricks notebook source
from pyspark.sql.functions import *
import time

# COMMAND ----------

class DataQuality:

  def __init__(self, source_table, target_table):

    self.source_table = source_table
    self.target_table = target_table
    self.id_quality_table = None
    self.filter_quality = None
    self.last_load_qlty_cfg_ts = None
    self.qlty_mngt_tables = [
      "mngt.dq_table_rule_stmts",
      "mngt.dq_table_qlty",
      "mngt.dq_rule_stmt"
    ]

    self.__load_data_quality_config()

  def __load_data_quality_config(self):

    tb_rl_df = spark.read.table("mngt.dq_table_rule_stmts")
    tb_df = spark.read.table("mngt.dq_table_qlty")
    tb_rl = spark.read.table("mngt.dq_rule_stmt")

    tb_rl_df = tb_rl_df.withColumnRenamed("id_tbl_qlty", "id_tbl_qlty_l")

    j1 = (
      tb_rl_df
      .join(other=tb_df, on=tb_rl_df.id_tbl_qlty_l == tb_df.id_tbl_qlty, how="left")
      .filter("active = true")
      .drop(*["active", "id_tbl_qlty_l"])
      .withColumnRenamed("id_stmt", "id_stmt_l")
    )

    map_rules = (
      j1
      .join(other=tb_rl, on=j1.id_stmt_l == tb_rl.id_stmt, how="left")
      .filter("active = true")
      .withColumn("table", concat_ws(".", col("target_tbl_schm"),col("target_tbl_nm")))
      .drop(*["active", "id_stmt_l", "target_tbl_schm", "target_tbl_nm"])
      .filter(f"upper(table) = '{self.target_table.upper()}'")
    )

    qlty_cfg = (
      map_rules
      .groupBy('id_tbl_qlty').agg(concat_ws(" and ", collect_list("stmt")).alias('qlty_filter'))
      .first()
    )

    if qlty_cfg != None:

      self.id_quality_table = qlty_cfg["id_tbl_qlty"]
      self.filter_quality = qlty_cfg["qlty_filter"]

    self.last_load_qlty_cfg_ts = time.time()


  def __is_quality_changed(self):

    for qlty_mngt_tbl in self.qlty_mngt_tables:

      last_modified = spark.sql(f"describe detail {qlty_mngt_tbl}").withColumn("last_modify_epoch", unix_timestamp(col("lastModified"))).first()["last_modify_epoch"]

      if last_modified > self.last_load_qlty_cfg_ts:
        return True
      
    return False
  

  def __register_rejected_rows(self, rejected_rows):

    rows_rej = (
      rejected_rows
      .fillna(value="<NULL>")   # Preenche campos nulos com a string '<NULL>' para que fiquem registrados na tabela de rejeitados, caso contrário não aparecem no json gerado
      .toJSON()                 # Converte os registros para JSON
      .collect()
    )   

    rows_rej = [{"origin_table":self.source_table, "id_tbl_qlty": self.id_quality_table, "filter_stmt": self.filter_quality, "json_rejected_row":jrow} for jrow in rows_rej]

    (
      spark.createDataFrame(rows_rej)
      .withColumn("process_timestamp", expr("current_timestamp()"))
      .withColumn("json_rejected_row", regexp_replace("json_rejected_row", '"<NULL>"', "null"))
      .select(["origin_table", "id_tbl_qlty", "filter_stmt", "json_rejected_row", "process_timestamp"])
      .write.mode("append")
      .insertInto("mngt.dq_rejected_rows")
    )


  def filter_df_with_quality_rules(self, input_df):

    if self.filter_quality == None:
      
      return input_df

    if self.__is_quality_changed():
    
      self.__load_data_quality_config()   

    # Obtem os registros aprovados na qualidade

    qlty_ok = input_df.filter(self.filter_quality)

    # Grava registros rejeitados

    qlty_rej = input_df.filter(f"not({self.filter_quality})")

    if not qlty_rej.isEmpty():

      self.__register_rejected_rows(qlty_rej)

    # Retorna os registros aprovados
    
    return qlty_ok


# COMMAND ----------

class Pii:

  def __init__(self, target_table):

    self.target_table = target_table
  
    self.last_load_pii_cfg_ts = None
    
    self.PII_CONFIG_TABLE = "mngt.pii_table_config"

    self.df_pii_cfg = None

    self.__load_pii_config()


  def __load_pii_config(self):
    
    self.df_pii_cfg = (
      spark.read.table(self.PII_CONFIG_TABLE)
      .filter(f"table_name = '{self.target_table}' and active = true")
      .select('protect_column','protect_operation')
    )

    self.last_load_pii_cfg_ts = time.time()


  def __is_pii_config_changed(self):

    last_modified = (
      spark.sql(f"describe detail {self.PII_CONFIG_TABLE}")
      .withColumn("last_modify_epoch", unix_timestamp(col("lastModified")))
      .first()["last_modify_epoch"]
    )    

    if last_modified > self.last_load_pii_cfg_ts:
      return True
      
    return False


  def apply_pii_operations_on_dataframe(self, input_df):

    if self.df_pii_cfg.isEmpty():

      return input_df
    
    if self.__is_pii_config_changed():
    
      self.__load_pii_config()

    column_types_dic = dict(input_df.dtypes)
    
    for pii_config in self.df_pii_cfg.collect():

      # No momento apenas colunas do tipo 'string' podem ter as operações aplicadas,
      # caso operações que suportem colunas de outros tipos forem adicionadas será
      # necessário fazer a verificação de data type antes de cada operação especifica.

      if column_types_dic[pii_config['protect_column']] != 'string':
        continue

      if pii_config['protect_operation'] == 'MASK_EMAIL':

        input_df = input_df.withColumn(pii_config['protect_column'], expr(f"regexp_replace({pii_config['protect_column']}, '(?<!^).(?=.+@)', '*')"))

      elif pii_config['protect_operation'] == 'MASK_PHONE':

        input_df = input_df.withColumn(pii_config['protect_column'], expr(f"regexp_replace({pii_config['protect_column']}, '(?<!^).(?!$)', '*')"))

      elif pii_config['protect_operation'] == 'HASH':

        input_df = input_df.withColumn(pii_config['protect_column'], expr(f"md5({pii_config['protect_column']})"))

      elif pii_config['protect_operation'] == 'MASK_GENERIC':

        input_df = input_df.withColumn(pii_config['protect_column'], expr(f"mask({pii_config['protect_column']})"))

      elif pii_config['protect_operation'] == 'REDACTED':

        input_df = input_df.withColumn(pii_config['protect_column'], lit("[REDACTED]"))

    return input_df

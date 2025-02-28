# Databricks notebook source
# MAGIC %run
# MAGIC ../utils/governance

# COMMAND ----------

from pyspark.sql.window import Window
from pyspark.sql.functions import *
from delta.tables import *
import os

# COMMAND ----------

class SilverProcessor:

  def __init__(self, silver_config):

    self.source_table = silver_config["source_table"]
    self.target_table = silver_config["target_table"]
    self.target_table_name = silver_config["target_table"].split(".")[1]
    self.dedup_keys = silver_config["dedup_keys"]
    self.dedup_orderby_column = silver_config["dedup_orderby_column"]
    self.trigger_interval_seconds = silver_config["trigger_interval_seconds"]
    self.max_bytes_per_trigger = silver_config["max_bytes_per_trigger"]
    self.column_transformations = silver_config["column_transformations"]

    self.base_path = os.environ.get("BASE_PATH")

    # Instancias necessárias para o processamento

    # Data quality
    self.data_qlty = DataQuality(self.source_table, self.target_table)

    # Pii
    self.pii = Pii(self.target_table)

    # Tabela delta de destino
    self.target_delta_table = DeltaTable.forName(spark, self.target_table)

    # Expecificação da janela de deduplicação
    self.ws_dedup = Window.partitionBy(self.dedup_keys).orderBy(desc(col(self.dedup_orderby_column).cast('timestamp')))


  def __exec_silver_operations(self, microDf, batchId):

    # Realiza a deduplicação de acordo com a configuração

    dedup_df = microDf.withColumn("rn", row_number().over(self.ws_dedup)).where("rn = 1").drop("rn")

    # Realiza as transformações configuradas

    col_tfs = self.column_transformations

    for col in col_tfs.keys():

      dedup_df = dedup_df.withColumn(col, expr(col_tfs[col]))

    # Aplica o processo de data quality

    # O data quality é aplicado nesse ponto pois aqui já temos todas as colunas
    # esperadas para a tabela de destino as quais são as encontradas no cadastro de data
    # quality

    dq_df = self.data_qlty.filter_df_with_quality_rules(dedup_df)

    # Aplica as operações de Pii

    pii_df = self.pii.apply_pii_operations_on_dataframe(dq_df)
    
    # Executa o merge na tabela alvo

    merge_key = [f"s.{key} = t.{key}" for key in self.dedup_keys]

    merge_key = (" and ").join(merge_key)

    (
      self.target_delta_table.alias('t')
      .merge(
        pii_df.alias('s'),
        f"{merge_key}"           
      )
      .whenMatchedUpdateAll()
      .whenNotMatchedInsertAll()
      .execute()
    )
      
  
  def start_silver_stream(self):

    stream = (
      spark.readStream
      .option("skipChangeCommits", "true")    # Ignora deletes e updates na tabela de origem, considera apenas inserts
      .table(self.source_table)
      .writeStream
      .queryName(f"STREAM_SILVER_{self.target_table_name.upper()}")
      .foreachBatch(self.__exec_silver_operations)
      .trigger(processingTime=f'{self.trigger_interval_seconds} seconds')
      .option("checkpointLocation", f"{self.base_path}/silver/{self.target_table_name}/_checkpoints/")
      .option("maxBytesPerTrigger", self.max_bytes_per_trigger)
      .start()
    )

    return stream

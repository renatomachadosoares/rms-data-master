# Databricks notebook source
import pyspark.sql.functions as F
from delta.tables import *

# COMMAND ----------

class ControlProcParams:

  def __init__(self):

    self.param_table_name = "mngt.control_proc_params"

    self.param_table_delta = DeltaTable.forName(spark, self.param_table_name)


  def get_param(self, param_group, param_name) -> str:

    ret = None

    param_value = (
      spark.read.table(self.param_table_name)
      .where(f"param_group = '{param_group}' and param_name = '{param_name}'")
      .select('param_value')
    )

    if not param_value.isEmpty():

      ret = param_value.first()['param_value']

    return ret


  def set_param(self, param_group:str, param_name:str, param_value:str):

    updt_df = spark.createDataFrame([{
      "param_group": param_group,
      "param_name": param_name,
      "param_value": param_value
    }], schema = "param_group string, param_name string, param_value string")

    updt_df = updt_df.withColumn("update_ts", F.current_timestamp())


    # Devido possíveis falha de concorrência de escrita na tabela de parâmetros o merge é executado até o sucesso

    while True:

      try:

        (
          self.param_table_delta.alias("t")
          .merge(
            updt_df.alias("s"),
            "t.param_group = s.param_group and t.param_name = s.param_name"
          )
          .whenMatchedUpdateAll()
          .whenNotMatchedInsertAll()
          .execute()
        )

        break

      except Exception as e:

        continue   

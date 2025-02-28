# Databricks notebook source
import os

# COMMAND ----------

class BronzeProcessor:

  def __init__(self, bronze_config):

    self.input_format = bronze_config["input_format"]
    self.read_options = bronze_config["read_options"]
    self.schema = bronze_config["schema"]      
    self.apply_expressions_on_input = bronze_config["apply_expressions_on_input"]    
    self.table_name = bronze_config["table_name"]

    self.base_path = os.environ.get("BASE_PATH")
    self.raw_input_path = f"{self.base_path}/raw/{self.table_name}"

  def start_bronze_stream(self):

    df = (
      spark.readStream
      .format(self.input_format)
      .schema(self.schema)
      .options(**self.read_options)
      .load(self.raw_input_path)
    )

    if self.apply_expressions_on_input != None:
      
      for expr in self.apply_expressions_on_input:

        df = df.selectExpr(expr)      

    stream = (
      df  
      .writeStream
      .queryName(f"STREAM_BRONZE_{self.table_name.upper()}")
      .outputMode("append")
      .option("checkpointLocation", f"{self.base_path}/bronze/{self.table_name}/_checkpoints/")
      .toTable(f"bronze.{self.table_name}")
    )

    return stream

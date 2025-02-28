# Databricks notebook source
# MAGIC %md
# MAGIC # GOLD - CLIENT PORTFOLIO

# COMMAND ----------

# MAGIC %run
# MAGIC ../utils/control_proc_params

# COMMAND ----------

import pyspark.sql.functions as F
from delta.tables import *
import time

# COMMAND ----------

TRIGGER_SECONDS = 60
CPP_PARAM_GROUP = "gold_client_portfolio"
CPP_PARAM_NAME = "last_process_unix_time"

# COMMAND ----------

cpp = ControlProcParams()

last_process = cpp.get_param(CPP_PARAM_GROUP, CPP_PARAM_NAME)

if last_process == None:
  last_process = 0    # Primeiro processamento
else:
  last_process = int(last_process)

target_table = DeltaTable.forName(spark, "gold.client_portfolio")

# COMMAND ----------

print(f"Iniciando processamento com parâmetro 'last_process' (unix_time) = '{last_process}'")

# COMMAND ----------

while True:

  start_process = int(time.time())

  df_orders = spark.read.table('silver.orders')
  df_quotes = spark.read.table('silver.stockquotes')

  # Obtem as alterações da carteira dos clientes desde a última iteração

  df_quotes_changed = (
    df_quotes.filter(f"unix_timestamp(requestedAt) > {last_process}").alias('q')
    .join(other=df_orders.alias("o"), on=F.expr("q.symbol = o.symbol"), how="left")
    .select("q.symbol", "q.longName", "o.quantity", "q.regularMarketPrice", "o.clientId")
  )

  # Obtem as alterações do valor das ações desde a última iteração

  df_orders_changed = (
    df_orders.filter(f"unix_timestamp(timestamp) > {last_process}").alias('o')
    .join(other=df_quotes.alias("q"), on=F.expr("q.symbol = o.symbol"), how="left")
    .select("q.symbol", "q.longName", "o.quantity", "q.regularMarketPrice", "o.clientId")
  )

  # Une as alterações de carteira e alterações de valor

  df_final = (
    df_orders_changed
    .unionAll(df_quotes_changed)
    .dropDuplicates()
    .selectExpr(
      "clientId as client_id",
      "symbol as stock_symbol", 
      "longName as stock_name", 
      "quantity", 
      "regularMarketPrice as market_price",
      "(quantity * regularMarketPrice) as total_value",
      "current_timestamp() as process_timestamp"
    )
  )

  # Faz o merge na tabela gold:

  if df_final.count() > 0:

    (
      target_table.alias('t')
      .merge(
        df_final.alias('s'),
        f"t.client_id = s.client_id and t.stock_symbol = s.stock_symbol"           
      )
      .whenMatchedUpdateAll()
      .whenNotMatchedInsertAll()
      .execute()
    )

  last_process = start_process

  cpp.set_param(CPP_PARAM_GROUP, CPP_PARAM_NAME, str(last_process))  # Persiste o timestamp do último processamento

  time.sleep(TRIGGER_SECONDS)

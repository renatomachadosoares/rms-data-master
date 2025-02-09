# Databricks notebook source
# MAGIC %md
# MAGIC # SILVER

# COMMAND ----------

# MAGIC %run
# MAGIC ./silver_processor

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Configuração dos processos silver

# COMMAND ----------

silver_configs = {
  ###################################################################
  # CEPS
  ###################################################################
  "ceps": {
    "source_table": "bronze.ceps",
    "target_table": "silver.ceps",
    "dedup_keys": ['cep'],
    "dedup_orderby_column": "requestedAt",
    "trigger_interval_seconds": "5",
    "max_bytes_per_trigger": "100m", # Config para evitar esgotamento de recurso, processo de Data Quality realiza collect     
    "column_transformations": {
      "ibge": "try_cast(ibge as integer)",
      "gia": "try_cast(gia as integer)",
      "ddd": "try_cast(ddd as integer)",
      "siafi": "try_cast(siafi as integer)",
      "requestedAt": "try_cast(requestedAt as timestamp)",
      "ingestion_time": "try_cast(ingestion_time as timestamp)",
      "process_timestamp": "current_timestamp()"
    }
  },
  ###################################################################
  # CLIENTS
  ###################################################################
  "clients": {
    "source_table": "bronze.clients",
    "target_table": "silver.clients",
    "dedup_keys": ['id'],
    "dedup_orderby_column": "updatetime",
    "trigger_interval_seconds": "5",
    "max_bytes_per_trigger": "100m",
    "column_transformations": {
      "id": "try_cast(id as integer)",
      "inv_prof_monthly_income": "try_cast(inv_prof_monthly_income as decimal(23,3))",
      "inv_prof_patrimony": "try_cast(inv_prof_patrimony as decimal(23,3))",
      "updatetime": "try_cast(updatetime as timestamp)",
      "ingestion_time": "try_cast(ingestion_time as timestamp)",
      "process_timestamp": "current_timestamp()"
    }
  },
  ###################################################################
  # ORDERS
  ###################################################################
  "orders": {
    "source_table": "bronze.orders",
    "target_table": "silver.orders",
    "dedup_keys": ['clientId', 'symbol'],
    "dedup_orderby_column": "timestamp",
    "trigger_interval_seconds": "5",
    "max_bytes_per_trigger": "100m",
    "column_transformations": {
      "SequenceNumber": "try_cast(SequenceNumber as bigint)",
      "clientId": "try_cast(clientId as integer)",
      "quantity": "try_cast(quantity as integer)",
      "timestamp": "try_cast(timestamp as timestamp)",
      "ingestion_time": "try_cast(ingestion_time as timestamp)",
      "process_timestamp": "current_timestamp()"
    }
  },
  ###################################################################
  # STOCK QUOTES
  ###################################################################
  "stockquotes": {
    "source_table": "bronze.stockquotes",
    "target_table": "silver.stockquotes",
    "dedup_keys": ['symbol'],
    "dedup_orderby_column": "requestedAt",
    "trigger_interval_seconds": "5",
    "max_bytes_per_trigger": "100m",
    "column_transformations": {      
      "regularMarketChange": "try_cast(regularMarketChange as decimal(23,3))",
      "regularMarketChangePercent": "try_cast(regularMarketChangePercent as decimal(6,3))",
      "regularMarketTime": "try_cast(regularMarketTime as timestamp)",
      "regularMarketPrice": "try_cast(regularMarketPrice as decimal(23,3))",
      "regularMarketDayHigh": "try_cast(regularMarketDayHigh as decimal(23,3))",
      "regularMarketDayLow": "try_cast(regularMarketDayLow as decimal(23,3))",
      "regularMarketVolume": "try_cast(regularMarketVolume as decimal(23,3))",
      "regularMarketPreviousClose": "try_cast(regularMarketPreviousClose as decimal(23,3))",
      "regularMarketOpen": "try_cast(regularMarketOpen as decimal(23,3))",
      "fiftyTwoWeekLow": "try_cast(fiftyTwoWeekLow as decimal(23,3))",
      "fiftyTwoWeekHigh": "try_cast(fiftyTwoWeekHigh as decimal(23,3))",
      "priceEarnings": "try_cast(priceEarnings as decimal(30,3))",
      "earningsPerShare": "try_cast(earningsPerShare as decimal(30,3))",
      "requestedAt": "try_cast(requestedAt as timestamp)",
      "ingestion_time": "try_cast(ingestion_time as timestamp)",
      "process_timestamp": "current_timestamp()"
    }
  }
}

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Processo CEPs

# COMMAND ----------

processor_ceps = SilverProcessor(silver_configs["ceps"])

processor_ceps.start_silver_stream()

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Processo Clients

# COMMAND ----------

processor_clients = SilverProcessor(silver_configs["clients"])

processor_clients.start_silver_stream()

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Processo Orders

# COMMAND ----------

processor_orders = SilverProcessor(silver_configs["orders"])

processor_orders.start_silver_stream()

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Processo Stock Quotes

# COMMAND ----------

processor_quotes = SilverProcessor(silver_configs["stockquotes"])

processor_quotes.start_silver_stream()

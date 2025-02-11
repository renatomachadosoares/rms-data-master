# Databricks notebook source
import os

# COMMAND ----------

base_path = os.environ.get("BASE_PATH")
catalog = os.environ.get("UNITY_CATALOG_NAME")

# COMMAND ----------

# MAGIC %md
# MAGIC #### SCHEMAS

# COMMAND ----------

spark.sql(f"create schema if not exists {catalog}.bronze")
spark.sql(f"create schema if not exists {catalog}.silver")
spark.sql(f"create schema if not exists {catalog}.gold")
spark.sql(f"create schema if not exists {catalog}.mngt")

# COMMAND ----------

# MAGIC %md
# MAGIC #### MANAGEMENT TABLES 

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Proc Control

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.mngt.control_proc_params (
    param_group STRING,
    param_name STRING,
    param_value STRING,
    update_ts TIMESTAMP)
  USING delta
  PARTITIONED BY (param_group)
  LOCATION '{base_path}/mngt/control_proc_params'
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Data Quality

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.mngt.dq_rule_stmt (
    id_stmt INTEGER,
    nm_stmt STRING,         
    stmt STRING,              --Regra propriamente dita, ex: "id_client is not null"
    active BOOLEAN)           --Statement está ativo?
  USING delta
  LOCATION '{base_path}/mngt/dq_rule_stmt'
""")

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.mngt.dq_table_qlty (
    id_tbl_qlty INTEGER,
    target_tbl_schm STRING,     --Schema/Database da tabela
    target_tbl_nm STRING,       --Nome da tabela
    active BOOLEAN)             --O cadastro está ativo?
  USING delta
  LOCATION '{base_path}/mngt/dq_table_qlty'
""")

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.mngt.dq_table_rule_stmts (
    id_tbl_qlty INTEGER,
    id_stmt INTEGER)
  USING delta
  LOCATION '{base_path}/mngt/dq_table_rule_stmts'
""")

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.mngt.dq_rejected_rows (
    origin_table STRING,
    id_tbl_qlty INTEGER,          -- ID do cadastro de qualidade que rejeitou o registro
    filter_stmt STRING,           -- Filtro de qualidade usado
    json_rejected_row STRING,     -- Representação JSON do registro rejeitado 
    process_timestamp TIMESTAMP)  -- Timestamp da rejeição do registro
  USING delta
  PARTITIONED BY (id_tbl_qlty)
  LOCATION '{base_path}/mngt/dq_rejected_rows'
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ###### PII

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.mngt.pii_table_config (
    table_name STRING,
    protect_column STRING,
    protect_operation STRING,
    active BOOLEAN)
  USING delta
  LOCATION '{base_path}/mngt/pii_table_config'
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Monitor

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.mngt.monitor_alerts (
    id_message string,
    origin string,
    message string,
    timestamp timestamp)
  USING DELTA 
  PARTITIONED BY (origin)
  LOCATION '{base_path}/mngt/monitor_alerts'         
""")

# COMMAND ----------

# MAGIC %md
# MAGIC #### BRONZE TABLES

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.bronze.ceps (
    cep STRING,
    logradouro STRING,
    complemento STRING,
    unidade STRING,
    bairro STRING,
    localidade STRING,
    uf STRING,
    estado STRING,
    regiao STRING,
    ibge STRING,
    gia STRING,
    ddd STRING,
    siafi STRING,
    requestedAt STRING,
    raw_input_file_name STRING,
    ingestion_time STRING,
    process_timestamp TIMESTAMP)
  USING delta
  LOCATION '{base_path}/bronze/ceps'
""")

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.bronze.clients (
    id STRING,
    name STRING,
    email STRING,
    phone STRING,
    postal_code STRING,
    doc_number STRING,
    doc_type STRING,
    account_number STRING,
    account_type STRING,
    inv_prof_type STRING,
    inv_prof_monthly_income STRING,
    inv_prof_patrimony STRING,
    inv_prof_objectives STRING,
    updatetime STRING,
    raw_input_file_name STRING,
    ingestion_time STRING,
    process_timestamp TIMESTAMP)
  USING delta
  LOCATION '{base_path}/bronze/clients'
""")

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.bronze.orders (
    SequenceNumber BIGINT,
    Offset STRING,
    EnqueuedTimeUtc STRING,
    SystemProperties MAP<STRING, STRUCT<member0: BIGINT, member1: DOUBLE, member2: STRING, member3: BINARY>>,
    Properties MAP<STRING, STRUCT<member0: BIGINT, member1: DOUBLE, member2: STRING, member3: BINARY>>,
    symbol STRING,
    clientId STRING,
    quantity STRING,
    timestamp STRING,
    raw_input_file_name STRING,
    ingestion_time STRING,
    process_timestamp TIMESTAMP)
  USING delta
  LOCATION '{base_path}/bronze/orders'
""")

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.bronze.stockquotes (
    currency STRING,
    shortName STRING,
    longName STRING,
    regularMarketChange STRING,
    regularMarketChangePercent STRING,
    regularMarketTime STRING,
    regularMarketPrice STRING,
    regularMarketDayHigh STRING,
    regularMarketDayRange STRING,
    regularMarketDayLow STRING,
    regularMarketVolume STRING,
    regularMarketPreviousClose STRING,
    regularMarketOpen STRING,
    fiftyTwoWeekRange STRING,
    fiftyTwoWeekLow STRING,
    fiftyTwoWeekHigh STRING,
    symbol STRING,
    priceEarnings STRING,
    earningsPerShare STRING,
    logourl STRING,
    requestedAt STRING,
    took STRING,
    raw_input_file_name STRING,
    ingestion_time STRING,
    process_timestamp TIMESTAMP)
  USING delta
  LOCATION '{base_path}/bronze/stockquotes'
""")

# COMMAND ----------

# MAGIC %md
# MAGIC #### SILVER TABLES

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.silver.ceps (
    cep STRING,
    logradouro STRING,
    complemento STRING,
    unidade STRING,
    bairro STRING,
    localidade STRING,
    uf STRING,
    estado STRING,
    regiao STRING,
    ibge INTEGER,
    gia INTEGER,
    ddd INTEGER,
    siafi INTEGER,
    requestedAt TIMESTAMP,
    raw_input_file_name STRING,
    ingestion_time TIMESTAMP,
    process_timestamp TIMESTAMP)
  USING delta
  LOCATION '{base_path}/silver/ceps'
""")

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.silver.clients (
    id INTEGER,
    name STRING,
    email STRING,
    phone STRING,
    postal_code STRING,
    doc_number STRING,
    doc_type STRING,
    account_number STRING,
    account_type STRING,
    inv_prof_type STRING,
    inv_prof_monthly_income DECIMAL(23, 3),
    inv_prof_patrimony DECIMAL(23, 3),
    inv_prof_objectives STRING,
    updatetime TIMESTAMP,
    raw_input_file_name STRING,
    ingestion_time TIMESTAMP,
    process_timestamp TIMESTAMP)
  USING delta
  LOCATION '{base_path}/silver/clients'
""")

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.silver.orders (
    SequenceNumber BIGINT,
    Offset STRING,
    EnqueuedTimeUtc STRING,
    SystemProperties MAP<STRING, STRUCT<member0: BIGINT, member1: DOUBLE, member2: STRING, member3: BINARY>>,
    Properties MAP<STRING, STRUCT<member0: BIGINT, member1: DOUBLE, member2: STRING, member3: BINARY>>,
    symbol STRING,
    clientId INTEGER,
    quantity INTEGER,
    timestamp TIMESTAMP,
    raw_input_file_name STRING,
    ingestion_time TIMESTAMP,
    process_timestamp TIMESTAMP)
  USING delta
  LOCATION '{base_path}/silver/orders'
""")

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.silver.stockquotes (
    currency STRING,
    shortName STRING,
    longName STRING,
    regularMarketChange DECIMAL(23,3),
    regularMarketChangePercent DECIMAL(6,3),
    regularMarketTime TIMESTAMP,
    regularMarketPrice DECIMAL(23,3),
    regularMarketDayHigh DECIMAL(23,3),
    regularMarketDayRange STRING,
    regularMarketDayLow DECIMAL(23,3),
    regularMarketVolume DECIMAL(23,3),
    regularMarketPreviousClose DECIMAL(23,3),
    regularMarketOpen DECIMAL(23,3),
    fiftyTwoWeekRange STRING,
    fiftyTwoWeekLow DECIMAL(23,3),
    fiftyTwoWeekHigh DECIMAL(23,3),
    symbol STRING,
    priceEarnings DECIMAL(30,3),
    earningsPerShare DECIMAL(30,3),
    logourl STRING,
    requestedAt TIMESTAMP,
    took STRING,
    raw_input_file_name STRING,
    ingestion_time TIMESTAMP,
    process_timestamp TIMESTAMP)
  USING delta
  LOCATION '{base_path}/silver/stockquotes'
""")

# COMMAND ----------

# MAGIC %md
# MAGIC #### GOLD TABLES

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.gold.client_portfolio (
    client_id INTEGER,  
    stock_symbol STRING, 
    stock_name STRING, 
    quantity INTEGER, 
    market_price DECIMAL(23,3),
    total_value DECIMAL(23,3),
    process_timestamp TIMESTAMP)
  USING delta
  LOCATION '{base_path}/gold/client_portfolio'
""")

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {catalog}.gold.client_portfolio_hist (
    client_id INTEGER,  
    stock_symbol STRING, 
    stock_name STRING, 
    quantity INTEGER, 
    market_price DECIMAL(23,3),
    total_value DECIMAL(23,3),
    snapshot_timestamp TIMESTAMP,
    snapshot_date DATE,
    process_timestamp TIMESTAMP)
  USING delta
  PARTITIONED BY (snapshot_date)
  LOCATION '{base_path}/gold/client_portfolio_hist'
""")

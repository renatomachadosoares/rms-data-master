# Databricks notebook source
# MAGIC %md
# MAGIC # BRONZE

# COMMAND ----------

# MAGIC %run
# MAGIC ./bronze_processor

# COMMAND ----------

from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Configuração dos processos bronze

# COMMAND ----------

# MAGIC %md
# MAGIC **Intruções de configuração**
# MAGIC
# MAGIC Cada processo deverá ser configurado com os seguintes parâmetros:
# MAGIC   
# MAGIC   **'table_name'**: Nome da tabela bronze de destino (não informar Database)
# MAGIC   
# MAGIC   **'input_format'**: O formato do arquivo de entrada da camada raw a ser processado 
# MAGIC                   (ex.: avro, csv, parquet)
# MAGIC   
# MAGIC   **'read_options'**: Dicionario com os parâmetros de configuração de leitura do arquivo. Informar dicionário vazio '{}' caso não seja necessário opções.
# MAGIC                   (ex.: {"header":"true"}). 
# MAGIC                   ver: https://sparkbyexamples.com/spark/spark-read-options/
# MAGIC   
# MAGIC   **'schema'**: Schema do arquivo de entrada. 
# MAGIC             ver: https://sparkbyexamples.com/pyspark/pyspark-structtype-and-structfield/
# MAGIC   
# MAGIC   **'apply_expressions_on_input'**: Lista de lista de expressões spark sql a serem aplicadas 
# MAGIC                                 nos dados de entrada. Cada lista será aplicada sequencialmente, 
# MAGIC                                 caso exista dependencia para a execução das expressões defina 
# MAGIC                                 de forma sequencial, como no exemplo:
# MAGIC
# MAGIC     `
# MAGIC     apply_expressions_on_input = [
# MAGIC       [
# MAGIC         # Cria coluna 'saldo_devedor' a partir de duas colunas existentes no schema
# MAGIC         "(valor_bem - valor_pago) as saldo_devedor"    
# MAGIC       ],
# MAGIC       [
# MAGIC         # Cria coluna 'valor_corrigido' a partir da coluna 'saldo_devedor' criada na lista de expressoes anterior
# MAGIC         "(saldo_devedor * 1.1) as valor_corrigido"
# MAGIC       ]
# MAGIC     ]
# MAGIC     `
# MAGIC
# MAGIC   **'trigger_stream_seconds'**: Intervalo do processamento streaming
# MAGIC

# COMMAND ----------

bronze_configs = {  
  ####################################################################
  # CEPS
  ####################################################################
  "ceps": {
    "table_name":"ceps",
    "input_format": "csv",
    "read_options": {"header":"true", "delimiter": ","},
    "schema": StructType(
        [
            StructField("cep", StringType(), True),
            StructField("logradouro", StringType(), True),
            StructField("complemento", StringType(), True),
            StructField("unidade", StringType(), True),
            StructField("bairro", StringType(), True),
            StructField("localidade", StringType(), True),
            StructField("uf", StringType(), True),
            StructField("estado", StringType(), True),
            StructField("regiao", StringType(), True),
            StructField("ibge", StringType(), True),
            StructField("gia", StringType(), True),
            StructField("ddd", StringType(), True),
            StructField("siafi", StringType(), True),
            StructField("requestedAt", StringType(), True),
            StructField("ingestion_time", StringType(), True),
        ]
    ),    
    "apply_expressions_on_input": [
      [
        "* except(dat_ref_carga)",
        "_metadata.file_path as raw_input_file_name",
        "current_timestamp() as process_timestamp"
      ]
    ],
    "trigger_stream_seconds": 60
  },
  ####################################################################
  # CLIENTS
  ####################################################################
  "clients": {
    "table_name":"clients",
    "input_format": "csv",
    "read_options": {"header":"true", "delimiter": ","},
    "schema": StructType(
        [
            StructField("id", StringType(), True),
            StructField("name", StringType(), True),
            StructField("email", StringType(), True),
            StructField("phone", StringType(), True),
            StructField("postal_code", StringType(), True),
            StructField("doc_number", StringType(), True),
            StructField("doc_type", StringType(), True),
            StructField("account_number", StringType(), True),
            StructField("account_type", StringType(), True),
            StructField("inv_prof_type", StringType(), True),
            StructField("inv_prof_monthly_income", StringType(), True),
            StructField("inv_prof_patrimony", StringType(), True),
            StructField("inv_prof_objectives", StringType(), True),
            StructField("updatetime", StringType(), True),
            StructField("ingestion_time", StringType(), True),
        ]
    ),    
    "apply_expressions_on_input": [
      [
        "* except(dat_ref_carga)",
        "_metadata.file_path as raw_input_file_name",
        "current_timestamp() as process_timestamp"
      ]
    ],
    "trigger_stream_seconds": 60
  },
  ####################################################################
  # ORDERS
  ####################################################################
  "orders": {
    "table_name":"orders",
    "input_format": "avro",
    "read_options": {},
    "schema": StructType(
        [
            StructField("SequenceNumber", LongType(), True),
            StructField("Offset", StringType(), True),
            StructField("EnqueuedTimeUtc", StringType(), True),
            StructField(
                "SystemProperties",
                MapType(
                    StringType(),
                    StructType(
                        [
                            StructField("member0", LongType(), True),
                            StructField("member1", DoubleType(), True),
                            StructField("member2", StringType(), True),
                            StructField("member3", BinaryType(), True),
                        ]
                    ),
                    True,
                ),
                True,
            ),
            StructField(
                "Properties",
                MapType(
                    StringType(),
                    StructType(
                        [
                            StructField("member0", LongType(), True),
                            StructField("member1", DoubleType(), True),
                            StructField("member2", StringType(), True),
                            StructField("member3", BinaryType(), True),
                        ]
                    ),
                    True,
                ),
                True,
            ),
            StructField("Body", BinaryType(), True),
        ]
    ),    
    "apply_expressions_on_input": [
      [
        "* except(Body, event_hub, topic, dat_ref_carga)",
        "from_json(cast(Body as string), 'symbol string, clientId string, quantity string, timestamp string') as Body"
      ],
      [
        "* except(Body)",
        "Body.*",
        "_metadata.file_path as raw_input_file_name",
        "timestamp as ingestion_time",
        "current_timestamp() as process_timestamp"    
      ]
    ],
    "trigger_stream_seconds": 60
  },
  ####################################################################
  # STOCKQUOTES
  ####################################################################
  "stockquotes": {
    "table_name":"stockquotes",
    "input_format": "csv",
    "read_options": {"header":"true", "delimiter": ","},
    "schema": StructType(
        [
            StructField("currency", StringType(), True),
            StructField("shortName", StringType(), True),
            StructField("longName", StringType(), True),
            StructField("regularMarketChange", StringType(), True),
            StructField("regularMarketChangePercent", StringType(), True),
            StructField("regularMarketTime", StringType(), True),
            StructField("regularMarketPrice", StringType(), True),
            StructField("regularMarketDayHigh", StringType(), True),
            StructField("regularMarketDayRange", StringType(), True),
            StructField("regularMarketDayLow", StringType(), True),
            StructField("regularMarketVolume", StringType(), True),
            StructField("regularMarketPreviousClose", StringType(), True),
            StructField("regularMarketOpen", StringType(), True),
            StructField("fiftyTwoWeekRange", StringType(), True),
            StructField("fiftyTwoWeekLow", StringType(), True),
            StructField("fiftyTwoWeekHigh", StringType(), True),
            StructField("symbol", StringType(), True),
            StructField("priceEarnings", StringType(), True),
            StructField("earningsPerShare", StringType(), True),
            StructField("logourl", StringType(), True),
            StructField("requestedAt", StringType(), True),
            StructField("took", StringType(), True),
            StructField("ingestion_time", StringType(), True),
        ]
    ),    
    "apply_expressions_on_input": [
      [
        "* except(dat_ref_carga)",
        "_metadata.file_path as raw_input_file_name",
        "current_timestamp() as process_timestamp"
      ]
    ],
    "trigger_stream_seconds": 60
  }
}

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Processo CEPs

# COMMAND ----------

processor_ceps = BronzeProcessor(bronze_configs["ceps"])

processor_ceps.start_bronze_stream()

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Processo Clients

# COMMAND ----------

processor_clients = BronzeProcessor(bronze_configs["clients"])

processor_clients.start_bronze_stream()

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Processo Orders
# MAGIC

# COMMAND ----------

processor_orders = BronzeProcessor(bronze_configs["orders"])

processor_orders.start_bronze_stream()

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Processo Stock Quotes

# COMMAND ----------

processor_quotes = BronzeProcessor(bronze_configs["stockquotes"])

processor_quotes.start_bronze_stream()

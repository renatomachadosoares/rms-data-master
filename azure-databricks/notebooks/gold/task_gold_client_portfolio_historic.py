# Databricks notebook source
# MAGIC %md
# MAGIC # GOLD HISTÓRICO - CLIENT PORTFOLIO

# COMMAND ----------

# MAGIC %run
# MAGIC ./historic_processor

# COMMAND ----------

# MAGIC %md
# MAGIC **NOTA:** O método 'run' da classe processadora de históricos é blocante e roda enquanto não for interrompido. Caso seja necessário ter o processamento de mais de uma tabela histórica o ideal é que se tenha uma task ou job para cada onde os parâmetros informados abaixo sejam usados como parâmetros destes.
# MAGIC Para este case os parâmetros estão HARD CODED na task pois só teremos uma única tabela histórica sendo processada. 

# COMMAND ----------

client_portfolio_hist = {
    "trigger_processor_minutes": 5,
    "historic_table":"gold.client_portfolio_hist",
    "source_table":"gold.client_portfolio",
    "snaphot_interval_minutes": 2
}

hist_proc = HistoricProcessor(client_portfolio_hist)

hist_proc.run()

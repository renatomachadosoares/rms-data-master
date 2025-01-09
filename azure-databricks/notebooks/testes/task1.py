# Databricks notebook source
BASE_PATH = "abfss://ctnlake@starmsdms810401.dfs.core.windows.net"

# COMMAND ----------

print("Teste de deploy de notebook!")

# COMMAND ----------

# Teste 1 - Criando um schema no Unity Catalog

spark.sql("CREATE SCHEMA IF NOT EXISTS datamaster.sch_bronze")

# COMMAND ----------

# Teste 2 - Criando uma tabela gerenciada no schema criado

spark.sql("CREATE TABLE IF NOT EXISTS datamaster.sch_bronze.teste_deploy_table (id INT, name STRING)") 

# COMMAND ----------

# Teste 3 - Criando uma tabela externa no schema criado

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS datamaster.sch_bronze.teste_deploy_table_external (id INT, name STRING)
    LOCATION '{BASE_PATH}/bronze/teste_deploy_table_external'
""")

# COMMAND ----------

# Teste 4 - Adicionando dados na tabela externa

spark.sql("INSERT INTO datamaster.sch_bronze.teste_deploy_table_external VALUES (1, 'Maria'), (2, 'Joao')")

# COMMAND ----------

# Teste 5 - Lendo um arquivo do storage

df = spark.read.csv(f"{BASE_PATH}/raw/clients", header=True, inferSchema=True)

df.display()

# COMMAND ----------

print("Fim do notebook de testes")
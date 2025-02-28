# Databricks notebook source
# MAGIC %md
# MAGIC ### Load Data Quality Rules

# COMMAND ----------

# MAGIC %md
# MAGIC Carrega as regras de qualidade mapeadas por tabela na camada silver. A configuração é estruturada pelo cadastro de regras, cadastro de tabelas e pelo mapeamento tabela -> regra. Regras podem ser reaproveitas realizando o compartilhamento de regras que se aplicam em mais de uma tabela usando o mapeamento adequado.
# MAGIC <br><br>
# MAGIC As regras aqui definidas e carregadas nas tabelas de cadastro de regras são utilizadas pela classe 'DataQuality' para aplicação das mesmas durante o processo de gravação dos dados provenientes da camada bronze na camada silver.
# MAGIC <br><br>
# MAGIC Regras novas podem ser cadastradas a qualquer momento, alterações no cadastro são detectadas pelo processador da camada silver e passam a ser aplicadas de forma imediata.
# MAGIC <br><br>
# MAGIC Regras editadas são aplicadas apenas à dados novos, o backlog já processado pela regra em sua forma antiga não é reprocessado a menos que o checkpoint da tabela silver alvo seja removido e reiniciado o processamento.
# MAGIC

# COMMAND ----------

# Cadastro de regras

dq_cfg_rule_stmts = [
  #(ID_REGRA,   NOME_REGRA,                         REGRA,                                              ATIVA)
  ( 1,          "CEP não nulo",                     "cep is not null",                                  "True"),
  ( 2,          "CEP tamanho 9",                    "len(cep) = 9",                                     "True"),
  ( 3,          "CEP complemento válido",           "complemento is not null",                          "False"),
  ( 4,          "CEP DDD válido",                   "try_cast(ddd as integer) < 77",                    "False"),
  ( 5,          "Data e hora da requisição válida", "try_cast(requestedAt as timestamp) is not null",   "True"),    # Regra compartilhada
  ( 6,          "Client id não nulo",               "id is not null",                                   "True"),
  ( 7,          "Nome válido",                      "name is not null and length(trim(name)) > 0",      "True"),
  ( 8,          "Campo 'updatetime' válido",        "try_cast(updatetime as timestamp) is not null",    "True"),
  ( 9,          "Client id não nulo",               "clientId is not null",                             "True"),
  (10,          "Stock symbol válido",              "symbol is not null and length(trim(symbol)) > 0",  "True"),    # Regra compartilhada
  (11,          "Campo 'timestamp' válido",         "try_cast(timestamp as timestamp) is not null",     "True")
]

# Cadastro de tabelas

dq_cfg_tables = [
  #(ID_TABELA,  SCHEMA,     TABELA,         ATIVO?)
  ( 1,          "silver",   "ceps",         "True"),
  ( 2,          "silver",   "clients",      "True"),
  ( 3,          "silver",   "orders",       "True"),
  ( 4,          "silver",   "stockquotes",  "True")
]

# Relacao tabela x regra

dq_cfg_table_rules = [
  #(ID_TABELA,  ID_REGRA)
  ( 1,          1),
  ( 1,          2),
  ( 1,          3),
  ( 1,          4),
  ( 1,          5),   # Regra compartilhada
  ( 2,          6),
  ( 2,          7),
  ( 2,          8),
  ( 3,          9),
  ( 3,          10),  # Regra compartilhada
  ( 3,          11),
  ( 4,          10),  # Regra compartilhada
  ( 4,          5),   # Regra compartilhada
]

# COMMAND ----------

df = spark.createDataFrame(dq_cfg_rule_stmts)

df.write.mode("overwrite").insertInto("mngt.dq_rule_stmt")


df = spark.createDataFrame(dq_cfg_tables)

df.write.mode("overwrite").insertInto("mngt.dq_table_qlty")


df = spark.createDataFrame(dq_cfg_table_rules)

df.write.mode("overwrite").insertInto("mngt.dq_table_rule_stmts")

# COMMAND ----------

# MAGIC %md
# MAGIC %md
# MAGIC ### Load Pii Operations Config

# COMMAND ----------

# MAGIC %md
# MAGIC Carrega as operações de confidencialidade aplicadas por tabela.
# MAGIC
# MAGIC O cadastro é feito por tabela e mapeia as operações de confidencialidade a serem aplicadas nas colunas cadastradas.
# MAGIC
# MAGIC É possivel associar 5 tipos diferentes de operações:
# MAGIC - MASK_GENERIC: aplica uma máscara genérica na coluna configurada.
# MAGIC - MASK_EMAIL: aplica máscara de email na coluna configurada.
# MAGIC - MASK_PHONE: aplica máscara de número de telefone na coluna configurada.
# MAGIC - HASH: aplica a função md5 na coluna configurada.
# MAGIC - REDACTED: faz uma simples substituição do valor da coluna pelo literal '[REDACTED]'
# MAGIC
# MAGIC As configurações aqui cadastradas são aplicadas pela classe 'Pii'.
# MAGIC

# COMMAND ----------

pii_config = [
  # ( table_name,         protect_column,     protect_operation,    active  )
  (   'silver.clients',   'email',            'MASK_EMAIL',         True  ),
  (   'silver.clients',   'phone',            'MASK_PHONE',         True  ),
  (   'silver.clients',   'doc_number',       'HASH',               True  ),
  (   'silver.clients',   'account_number',   'MASK_GENERIC',       True  ),
  (   'silver.clients',   'account_type',     'REDACTED',           True  )
]

# COMMAND ----------

df = spark.createDataFrame(pii_config, schema="table_name string, protect_column string, protect_operation string, active boolean")

df_accepted = df.filter("protect_operation in ('MASK_EMAIL','MASK_PHONE','HASH','MASK_GENERIC', 'REDACTED')")

df_not_accepted = df.filter("protect_operation not in ('MASK_EMAIL','MASK_PHONE','HASH','MASK_GENERIC', 'REDACTED')")

df_accepted.write.mode("overwrite").insertInto("mngt.pii_table_config")

if df_not_accepted.count() > 0:

  print("\nOs seguintes registros de configuração não atendem as operações válidas ['MASK_EMAIL','MASK_PHONE','HASH','MASK_GENERIC', 'REDACTED']")

  df_not_accepted.show()

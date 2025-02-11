# Databricks notebook source
import os

# COMMAND ----------

base_path = os.environ.get("BASE_PATH")
unity_credential = os.environ.get("UNITY_CREDENTIAL_NAME")

# Cria as external locations no unity
          
spark.sql(f'''
    CREATE EXTERNAL LOCATION IF NOT EXISTS `ext-loc-raw`
    URL '{base_path}/raw'
    WITH (STORAGE CREDENTIAL `{unity_credential}`)
''')

spark.sql(f'''
    CREATE EXTERNAL LOCATION IF NOT EXISTS `ext-loc-bronze`
    URL '{base_path}/bronze'
    WITH (STORAGE CREDENTIAL `{unity_credential}`)
''')

spark.sql(f'''
    CREATE EXTERNAL LOCATION IF NOT EXISTS `ext-loc-silver`
    URL '{base_path}/silver'
    WITH (STORAGE CREDENTIAL `{unity_credential}`)
''')

spark.sql(f'''
    CREATE EXTERNAL LOCATION IF NOT EXISTS `ext-loc-gold`
    URL '{base_path}/gold'
    WITH (STORAGE CREDENTIAL `{unity_credential}`)
''')

spark.sql(f'''
    CREATE EXTERNAL LOCATION IF NOT EXISTS `ext-loc-mngt`
    URL '{base_path}/mngt'
    WITH (STORAGE CREDENTIAL `{unity_credential}`)
''')

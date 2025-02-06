# Databricks notebook source
BASE_PATH = "abfss://ctnlake@starmsdms810401.dfs.core.windows.net"

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS `ext-loc-raw`
# MAGIC URL 'abfss://ctnlake@starmsdms810401.dfs.core.windows.net/raw'
# MAGIC WITH (STORAGE CREDENTIAL `unity-credential`);
# MAGIC
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS `ext-loc-bronze`
# MAGIC URL 'abfss://ctnlake@starmsdms810401.dfs.core.windows.net/bronze'
# MAGIC WITH (STORAGE CREDENTIAL `unity-credential`);
# MAGIC
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS `ext-loc-silver`
# MAGIC URL 'abfss://ctnlake@starmsdms810401.dfs.core.windows.net/silver'
# MAGIC WITH (STORAGE CREDENTIAL `unity-credential`);
# MAGIC
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS `ext-loc-gold`
# MAGIC URL 'abfss://ctnlake@starmsdms810401.dfs.core.windows.net/gold'
# MAGIC WITH (STORAGE CREDENTIAL `unity-credential`);
# MAGIC
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS `ext-loc-mngt`
# MAGIC URL 'abfss://ctnlake@starmsdms810401.dfs.core.windows.net/mngt'
# MAGIC WITH (STORAGE CREDENTIAL `unity-credential`);

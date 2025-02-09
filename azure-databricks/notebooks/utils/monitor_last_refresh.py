# Databricks notebook source
# MAGIC %md
# MAGIC #### Monitor Last Refresh

# COMMAND ----------

# MAGIC %md
# MAGIC O Monitor Last refresh monitora as tabelas definidas no parâmetro de configuração verificando seu último timestamp de atualização e alertando em caso de atrasos.

# COMMAND ----------

pip install croniter

# COMMAND ----------

from croniter import croniter
import datetime, time
from pyspark.sql.functions import *

# COMMAND ----------

class MonitorLastRefresh():

  def __init__(self, alert_sender: InterfaceAlertSender, list_table_monit_config, cron_execution_config):

    self.TIME_CHECK_CRON_SECONDS = 5

    self.alert_sender = alert_sender
    self.list_table_monit_config = list_table_monit_config
    self.cron_execution_config = cron_execution_config


  def start_monitor(self):

    croniter_itr = croniter(self.cron_execution_config, datetime.datetime.now())

    next_exec = croniter_itr.get_next(datetime.datetime)

    # Laço do cron

    while True:  

      # Verifica se a próxima execução do cron está no horário

      now = datetime.datetime.now()

      if now >= next_exec:
        
        print(f"Run verifications on {datetime.datetime.now()}...")

        self.__run_verification()

        # Atualiza a proxima execução do cron

        next_exec = croniter_itr.get_next(datetime.datetime)     
      
      # Dorme até a próxima verificação de alcance do cron

      time.sleep(self.TIME_CHECK_CRON_SECONDS)


  def __run_verification(self):

    monit_results = []

    for table_m in self.list_table_monit_config:

      table = table_m["table_to_monitoring"]
      delay_to_alert = table_m["delay_to_alert"]
      delay_to_alert_unit = table_m["delay_to_alert_unit"]

      res = (
        spark.sql(f"describe detail {table}")
        .selectExpr(
          f"'{table}' as table", 
          "lastModified as last_modified", 
          f"lastModified < current_timestamp() - interval {delay_to_alert} {delay_to_alert_unit} as delayed",
          f"'last_modified > {delay_to_alert} {delay_to_alert_unit.upper()}' delay_trigger_config"
        )
        .first()
      )

      monit_results.append(res)

    delayed_df = spark.createDataFrame(monit_results).filter("delayed = true")

    self.__send_alerts(delayed_df)


  def __send_alerts(self, delayed_df):

    for delayed in delayed_df.collect():

      self.alert_sender.send_alert_message(f"Tabela '{delayed['table']}' atrasada! Última atualização em '{delayed['last_modified']}' - trigger alerta configurado: [{delayed['delay_trigger_config']}]")

# Databricks notebook source
# MAGIC %md
# MAGIC #### Monitor Data Flow

# COMMAND ----------

# MAGIC %md
# MAGIC O Monitor Data Flow acompanha os tempos de um fluxo de dados de ponta a ponta, de acordo com a configuração definida através de 'steps'. Cada step configurado indica quais tabelas dentro do fluxo devem ser monitoradas e o tempo máximo de atraso em relação ao step anterior. Entre cada step é verificado qual a atualização mais recente entre as tabelas definidas e comparado com a atualização mais recente entre as tabelas do passo imediatamento posterior, caso exista uma diferença que ultrapasse o limite estabelecido entre os dois steps é disparado uma notificação de alerta. O objetivo deste monitor é detectar gargalos no processamento entre os steps definidos.

# COMMAND ----------

from croniter import croniter
import datetime, time
from pyspark.sql.functions import *

# COMMAND ----------

class MonitorDataFlow():

  def __init__(self, alert_sender: InterfaceAlertSender, flow_config, cron_execution_config):

    self.TIME_CHECK_CRON_SECONDS = 5

    self.alert_sender = alert_sender
    self.flow_config = flow_config
    self.cron_execution_config = cron_execution_config


  def start_monitor(self):

    croniter_itr = croniter(self.cron_execution_config, datetime.datetime.now())

    next_exec = croniter_itr.get_next(datetime.datetime)

    # Laço do cron

    while True:  

      # Verifica se a próxima execução do cron está no horário

      now = datetime.datetime.now()

      if now >= next_exec:

        self.__run_verification()

        # Atualiza a proxima execução do cron

        next_exec = croniter_itr.get_next(datetime.datetime)     
      
      # Dorme até a próxima verificação de alcance do cron

      time.sleep(self.TIME_CHECK_CRON_SECONDS)


  def __run_verification(self):

    step_previous = None
    lastModified_step_previous = None
    alerts = []

    steps_order = sorted(self.flow_config['steps'], key=lambda step: step['sequence'])
    
    for step in steps_order:        

      step_seq = step['sequence'] 
      step_name = step['step_name']
      max_delay_from_previous_step_seconds = step['max_delay_from_previous_step_seconds']
      lineage_tables = step['lineage_tables']

      max_lastModified = datetime.datetime(1, 1, 1, 0, 0, 0)

      for table in lineage_tables:

        last = (
          spark.sql(f"describe history {table} limit 500")
          .where("operation in ('WRITE','MERGE','UPDATE','INSERT','STREAMING UPDATE')")
          .where("operationMetrics.numOutputRows > 0")
          .selectExpr("max(timestamp) as max_timestamp")
          .first()['max_timestamp']
        )

        if last is not None and last > max_lastModified:
          max_lastModified = last

      if lastModified_step_previous is not None:
          
        diff = (max_lastModified - lastModified_step_previous).total_seconds()

        if diff > max_delay_from_previous_step_seconds:

          alerts.append(f"O step '{step_name}' apresenta um atraso de {diff} segundos em relação ao step '{step_previous}'")

      step_previous = step_name
      lastModified_step_previous = max_lastModified

    if len(alerts) > 0:
      
      self.__send_alerts(" | ".join(alerts))


  def __send_alerts(self, message):

    self.alert_sender.send_alert_message(f"Atraso(s) detectado(s) no fluxo '{self.flow_config['flow_name']}' - [{message}]")

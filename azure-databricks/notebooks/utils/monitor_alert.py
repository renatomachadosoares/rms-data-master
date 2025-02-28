# Databricks notebook source
# MAGIC %md
# MAGIC #### Monitor Alert

# COMMAND ----------

import abc

# COMMAND ----------

# MAGIC %md
# MAGIC Interface Alert Sender: define o comportamento padrão de um 'enviador' de mensagens de alerta de monitoramento. A partir dessa interface podem ser implementadas classes concretas que fazem envio de mensagens usando o Teams, Slack, email, Kafka, ou até mesmo uma tabela, que é o utilizado no case.

# COMMAND ----------

class InterfaceAlertSender(abc.ABC):

  def __init__(self, config: dict):
    self.config = config

  @abc.abstractmethod
  def send_alert_message(self, message:str):
    raise NotImplementedError

# COMMAND ----------

# MAGIC %md
# MAGIC Para o case Data Master foi implementada a classe abaixo que faz envio de mensagens para uma tabela delta. Para acompanhar as mensagens de alerta basta consultar a tabela 'mngt.monitor_alerts'.

# COMMAND ----------

class AlertUsingMonitorAlertsTable(InterfaceAlertSender):

  def __init__(self, config: dict):

    super().__init__(config)

    self.TABLE_ALERT_MESSAGES = "mngt.monitor_alerts"


  def send_alert_message(self, message:str):

    monitor_name = self.config["monitor_name"]
    message = message.replace("'", '"')

    spark.sql(f"""
      insert into {self.TABLE_ALERT_MESSAGES} 
      (
        id_message,
        origin,
        message,
        timestamp
      )
      values (
        '{monitor_name.upper()}' || '_' || unix_timestamp(),
        '{monitor_name}',
        '{message}',
        current_timestamp()
      )
    """)

# Databricks notebook source
# MAGIC %md
# MAGIC ### Monitoramento

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC O monitoramento realizado é implementado pela classe 'MonitorLastRefresh' que verifica a última atualização das tabelas e dispara mensagens de alerta nos casos onde a tabela tenha sido atualizada em um período maior que o tempo de atraso máximo definido em sua configuração. A configuração é baseada em dicionário e possui uma lista de entradas que informam a tabela a ser monitorada e o tempo máximo de atraso aceitável.
# MAGIC O sistema de mensagens utilizado é baseado na classe 'AlertUsingMonitorAlertsTable', onde as mensagens de alerta são enviadas/gravadas na tabela 'mngt.monitor_alerts'.

# COMMAND ----------

# MAGIC %run
# MAGIC ../utils/monitor_alert

# COMMAND ----------

# MAGIC %run
# MAGIC ../utils/monitor_last_refresh

# COMMAND ----------

# Configurações do monitor 'Last Refresh'

list_config_mon_last_refresh = [
  {
    "table_to_monitoring": "bronze.ceps",
    "delay_to_alert": 10,
    "delay_to_alert_unit": 'seconds'
  },
  {
    "table_to_monitoring": "silver.ceps",
    "delay_to_alert": 10,
    "delay_to_alert_unit": 'days'
  },
  {
    "table_to_monitoring": "bronze.clients",
    "delay_to_alert": 10,
    "delay_to_alert_unit": 'hours'
  },
  {
    "table_to_monitoring": "silver.clients",
    "delay_to_alert": 10,
    "delay_to_alert_unit": 'months'
  }  
]

# COMMAND ----------

# Instancia o alert sender 'AlertUsingMonitorAlertsTable'

alert_sender_config = {
  "monitor_name": "monitor_last_refresh"
}

alert_sender = AlertUsingMonitorAlertsTable(alert_sender_config)


# Instancia o Monitor de última atualização

cron_execution_config = "*/15 * * * *"   # Executa a cada 15 minutos

mon_refresh = MonitorLastRefresh(alert_sender, list_config_mon_last_refresh, cron_execution_config)

mon_refresh.start_monitor()

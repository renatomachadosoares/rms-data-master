# Databricks notebook source
# MAGIC %run
# MAGIC ../utils/monitor_alert

# COMMAND ----------

# MAGIC %run
# MAGIC ../utils/monitor_data_flow

# COMMAND ----------

flow_monitors = {
    "client_portfolio": {
        "flow_name":"client_portfolio",
        "steps": [
            {
                "sequence": 1,
                "step_name": "bronze",
                "lineage_tables":[
                    "bronze.orders",
                    "bronze.stockquotes"
                ],
                "max_delay_from_previous_step_seconds": None        # Não se aplica para o primeiro passo
            },
            {
                "sequence": 2,
                "step_name": "silver",
                "lineage_tables":[
                    "silver.orders",
                    "silver.stockquotes"
                ],
                "max_delay_from_previous_step_seconds": 30
            },
            {
                "sequence": 3,
                "step_name": "gold",
                "lineage_tables":[
                    "gold.client_portfolio"
                ],
                "max_delay_from_previous_step_seconds": 30
            }
        ],
        "check_interval_minutes": 2
    }
}

# COMMAND ----------

# Obtem as configurações do monitor de fluxo 'client_portfolio'

config = flow_monitors["client_portfolio"]


# Instancia o alert sender 'AlertUsingMonitorAlertsTable'

alert_sender_config = {
  "monitor_name": f"monitor_data_flow_{config['flow_name']}"
}

alert_sender = AlertUsingMonitorAlertsTable(alert_sender_config)


# Instancia o Monitor Data Flow

cron_execution_config = "*/15 * * * *"   # Executa a cada 15 minutos

mon_data_flow = MonitorDataFlow(alert_sender, config, cron_execution_config)

mon_data_flow.start_monitor()

# Databricks notebook source
# MAGIC %run
# MAGIC ../utils/control_proc_params

# COMMAND ----------

import pyspark.sql.functions as F
from delta.tables import *
import time
import datetime
from pyspark.errors.exceptions.captured import AnalysisException

# COMMAND ----------

class HistoricProcessor:

  def __init__(self, historic_config):

    self.trigger_processor_minutes = historic_config["trigger_processor_minutes"]
    self.historic_table = historic_config["historic_table"]
    self.source_table = historic_config["source_table"]
    self.snaphot_interval_minutes = historic_config["snaphot_interval_minutes"]

    self.source_delta = DeltaTable.forName(spark, self.source_table)
    self.hist_delta = DeltaTable.forName(spark, self.historic_table)

    self.cpp = ControlProcParams()

    self.cpp_param_group = f"{self.historic_table}"


  def __round_timestamp(self, timestamp, round_minutes):

    round_ts = timestamp + datetime.timedelta(minutes = round_minutes)
    round_ts = round_ts.replace(second = 0, microsecond = 0)

    min_add = (round_minutes - round_ts.minute % round_minutes) % round_minutes
    round_ts += datetime.timedelta(minutes = min_add)

    return round_ts


  def __get_start_snapshot(self):

    last_delta_hist_ts_proc = self.cpp.get_param(self.cpp_param_group, "last_snapshot_processed")

    if last_delta_hist_ts_proc == None:

      # Obtem o timestamp da primeira versão delta disponível da tabela fonte

      first_hst_df = (
        self.source_delta
        .history()
        .orderBy(F.col('version').asc())
        .limit(1)
        .select("timestamp")
      )

      start_snapshot = self.__round_timestamp(first_hst_df.first()["timestamp"], self.snaphot_interval_minutes)

    else:

      start_snapshot = datetime.datetime.strptime(last_delta_hist_ts_proc, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=self.snaphot_interval_minutes)
    
    return start_snapshot

    
  def run(self):
    
    cur_snap = self.__get_start_snapshot()

    print(f"Iniciando carga histórica para o snapshot = '{cur_snap}'")

    while True:

      print("-"*150)
      print(f"+ Iniciando nova iteração de carga histórica em '{datetime.datetime.now()}'...")

      while True:

        # Tenta ler a tabela na versão histórica com timestamp 'cur_snap'

        print(f"- Processando carga histórica snapshot '{cur_snap}'")

        try:

          hist_snap_df = (
            spark.read.option("timestampAsOf", str(cur_snap))
            .table("gold.client_portfolio")
            .selectExpr(
              "* except(process_timestamp)",
              f"'{str(cur_snap)}' as snapshot_timestamp",
              f"cast('{str(cur_snap)}' as date) as snapshot_date",
              f"current_timestamp() as process_timestamp"
            )
          )

          # Faz a carga histórica com merge para evitar duplicidade de registros históricos no caso onde o parâmetro
          # de processamento 'last_snapshot_processed' tenha sido perdido ou corrompido

          (
            self.hist_delta.alias("t")
            .merge(
              source = hist_snap_df.alias("s"),
              condition= '''
                t.snapshot_timestamp = s.snapshot_timestamp 
                and t.snapshot_date = s.snapshot_date      --prunning partitions
              '''
            )
            .whenNotMatchedInsertAll()
            .execute()
          )

        except AnalysisException as e:

          print(f"- O snapshot '{cur_snap}' ainda não está disponível!")
          print("- Encerrando iteração de carga histórica...")

          break

        # Persiste o timestamp historico processado na tabela de controle e incrementa para a nova iteração

        self.cpp.set_param(self.cpp_param_group, "last_snapshot_processed", str(cur_snap))

        cur_snap = cur_snap + datetime.timedelta(minutes=self.snaphot_interval_minutes)
      

      # Dorme até a próxima iteração do processo de carga histórica

      print(f"\nAguardando a próxima iteração da trigger de {self.trigger_processor_minutes} minutos...")
      time.sleep(self.trigger_processor_minutes * 60)  

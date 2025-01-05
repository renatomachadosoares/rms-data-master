import datetime
import json
import logging
import random
import asyncio
import pyodbc

import azure.functions as func
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.identity.aio import DefaultAzureCredential

# Event Hubs

EVENT_HUB_FULLY_QUALIFIED_NAMESPACE = "evhnmprmsdms810401.servicebus.windows.net"
EVENT_HUB_NAME = "evhorders"

credential = DefaultAzureCredential()

# SQL Database

SERVER = "sdbrmsdms810401.database.windows.net"
DATABASE = "CUSTOMER"
USER = "sqldbrms_usr"
PWD = f"pwdD8*DMS#"


# Functions

app = func.FunctionApp()

###############################################################
# FUNCAO DE GERACAO DO VALOR DAS ACOES
###############################################################

@app.route(route="StockQuotes", auth_level=func.AuthLevel.ANONYMOUS)
def GetPrices(req: func.HttpRequest) -> func.HttpResponse:

    now = datetime.datetime.utcnow()
    request_time = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'

    quotes = {
        "results": [
            {
            "currency": "BRL",
            "shortName": "SANTANDER BRUNT",
            "longName": "Banco Santander (Brasil) S.A.",
            "regularMarketChange": -0.14,
            "regularMarketChangePercent": -0.589,
            "regularMarketTime": "2024-12-27T21:07:45.000Z",
            "regularMarketPrice": round(random.uniform(20.0, 30.0), 2),#23.63,
            "regularMarketDayHigh": 0,
            "regularMarketDayRange": "0 - 0",
            "regularMarketDayLow": 0,
            "regularMarketVolume": 0,
            "regularMarketPreviousClose": 23.77,
            "regularMarketOpen": 23.61,
            "fiftyTwoWeekRange": "0 - 32.34",
            "fiftyTwoWeekLow": 0,
            "fiftyTwoWeekHigh": 32.34,
            "symbol": "SANB11",
            "priceEarnings": None,
            "earningsPerShare": None,
            "logourl": "https://s3-symbol-logo.tradingview.com/santander--big.svg"
            },
            {
            "currency": "BRL",
            "shortName": "CVC BRASIL  ON      NM",
            "longName": "CVC Brasil Operadora e Agência de Viagens S.A.",
            "regularMarketChange": -0.03,
            "regularMarketChangePercent": -2.098,
            "regularMarketTime": "2024-12-27T23:26:04.000Z",
            "regularMarketPrice": round(random.uniform(1.0, 2.0), 2), #1.4,
            "regularMarketDayHigh": 0,
            "regularMarketDayRange": "0 - 0",
            "regularMarketDayLow": 0,
            "regularMarketVolume": 0,
            "regularMarketPreviousClose": 1.43,
            "regularMarketOpen": 1.55,
            "fiftyTwoWeekRange": "0 - 3.6",
            "fiftyTwoWeekLow": 0,
            "fiftyTwoWeekHigh": 3.6,
            "symbol": "CVCB3",
            "priceEarnings": None,
            "earningsPerShare": -0.2218071,
            "logourl": "https://s3-symbol-logo.tradingview.com/cvc-brasil-on-nm--big.svg"
            },
            {
            "currency": "BRL",
            "shortName": "PETROBRAS   PN  EDJ N2",
            "longName": "Petróleo Brasileiro S.A. - Petrobras",
            "regularMarketChange": -0.11,
            "regularMarketChangePercent": -0.308,
            "regularMarketTime": "2024-12-27T21:07:46.000Z",
            "regularMarketPrice": round(random.uniform(30.0, 40.0), 2), #35.66,
            "regularMarketDayHigh": 0,
            "regularMarketDayRange": "0 - 0",
            "regularMarketDayLow": 0,
            "regularMarketVolume": 0,
            "regularMarketPreviousClose": 35.77,
            "regularMarketOpen": 37.63,
            "fiftyTwoWeekRange": "0 - 42.94",
            "fiftyTwoWeekLow": 0,
            "fiftyTwoWeekHigh": 42.94,
            "symbol": "PETR4",
            "priceEarnings": 5.6254196935474,
            "earningsPerShare": 6.5524291,
            "logourl": "https://s3-symbol-logo.tradingview.com/brasileiro-petrobras--big.svg"
            },
            {
            "currency": "BRL",
            "shortName": "METALFRIO   ON      NM",
            "longName": "Metalfrio Solutions S.A.",
            "regularMarketChange": 68.5,
            "regularMarketChangePercent": 30.995,
            "regularMarketTime": "2024-12-27T21:15:00.000Z",
            "regularMarketPrice": round(random.uniform(250.0, 300.0), 2), #289.5,
            "regularMarketDayHigh": 0,
            "regularMarketDayRange": "0 - 0",
            "regularMarketDayLow": 0,
            "regularMarketVolume": 0,
            "regularMarketPreviousClose": 221,
            "regularMarketOpen": 154.9,
            "fiftyTwoWeekRange": "0 - 399.89",
            "fiftyTwoWeekLow": 0,
            "fiftyTwoWeekHigh": 399.89,
            "symbol": "FRIO3",
            "priceEarnings": 35.5052298243931,
            "earningsPerShare": 5.2183679,
            "logourl": "https://brapi.dev/favicon.svg"
            }
        ],
        "requestedAt": request_time,
        "took": "0ms"
    }

    return func.HttpResponse(
             json.dumps(quotes),
             mimetype="application/json",
             status_code=200
        )


###############################################################
# FUNCAO DE ENVIO DO STATUS DA CARTEIRA DO CLIENTE PARA UMA 
# DADA AÇÂO COM A QUANTIDADE DESSE PAPEL
# (ESSA ABORDAGEM É MELHOR QUE A DE ORDENS DE COMPRA E VENDA
# DE ACOES PENSADA INICIALMENTE, DIMINUI A COMPLEXIDADE DOS DADOS 
# DE EXEMPLO, ASSIM NO LAKE TEREMOS A POSICAO DO CLIENTE BASEADO 
# NA SUA QUANTIDADE DE PAPEIS)
###############################################################

async def run():

    now = datetime.datetime.utcnow()

    producer = EventHubProducerClient(
        fully_qualified_namespace=EVENT_HUB_FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENT_HUB_NAME,
        credential=credential,
    )
    async with producer:
        
        event_data_batch = await producer.create_batch()

        symbols = ["SANB11", "CVCB3", "PETR4", "FRIO3"]

        event_data_batch.add(EventData(json.dumps({"symbol":f"{random.choice(symbols)}", "clientId":"1", "quantity":random.randint(1, 10), "timestamp":f"{now}"})))
        event_data_batch.add(EventData(json.dumps({"symbol":f"{random.choice(symbols)}", "clientId":"2", "quantity":random.randint(1, 10), "timestamp":f"{now}"})))
        event_data_batch.add(EventData(json.dumps({"symbol":f"{random.choice(symbols)}", "clientId":"3", "quantity":random.randint(1, 10), "timestamp":f"{now}"})))
    
        await producer.send_batch(event_data_batch)

        await credential.close()


@app.timer_trigger(schedule="0 */10 * * * *",     # A cada 10 minutos
              arg_name="ordersGenerator",
              run_on_startup=True) 
def GenerateOrders(ordersGenerator: func.TimerRequest) -> None:

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    
    if ordersGenerator.past_due:
        logging.info('The timer is past due!')
    
    logging.info(f"Enviando ordens para o event hub em '{utc_timestamp}'")

    asyncio.run(run())



###############################################################
# FUNCAO QUE CRIA A BASE DE CLIENTES
###############################################################

@app.route(route="CreateDbCustomer", auth_level=func.AuthLevel.ANONYMOUS)
def CreateDbCustomer(req: func.HttpRequest) -> func.HttpResponse:

    now = datetime.datetime.utcnow()

    logging.info(f"Criando a base de dados de clientes as '{now}'")    
        
    try:

        cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};PORT=1433;SERVER='+SERVER+';PORT=1443;DATABASE='+DATABASE+';UID='+USER+';PWD='+ PWD)

    except Exception as e:

        logging.info(f"Erro ao tentar acessar o banco: {e}")

    cursor = cnxn.cursor()

    # Criando as tabelas
    
    client_table = '''
        CREATE TABLE clients (
            id varchar(5) NOT NULL,
            name varchar(30) NOT NULL,
            email varchar(50) NOT NULL,
            phone varchar(20) NOT NULL,
            postal_code varchar(15) NOT NULL,
            doc_number varchar(15) NOT NULL,
            doc_type varchar(10) NOT NULL,
            account_number varchar(15) NOT NULL,
            account_type varchar(15) NOT NULL,
            inv_prof_type varchar(15) NOT NULL,
            inv_prof_monthly_income decimal(15,3) NOT NULL,
            inv_prof_patrimony decimal(15,3) NOT NULL,
            inv_prof_objectives varchar(100),
            updatetime datetime2 NOT NULL
        )
    '''

    control_table = '''
        CREATE TABLE ingest_control (
            table_ingested varchar(50) NOT NULL,
            ref_timestamp_column varchar(50) NOT NULL,
            last_ref_timestamp_ingested datetime2 NOT NULL,
            ingest_execution_timestamp datetime2
        )
    '''

    tables_DDL = [
        {
            "table_name": "clients",
            "ddl_stmt": client_table
        },
        {
            "table_name": "ingest_control",
            "ddl_stmt": control_table
        }
    ]

    for table in tables_DDL:

        try:
            
            logging.info(f'Creating table {table["table_name"]}...')

            cursor.execute(table["ddl_stmt"])

        except Exception as e:

            logging.info(f"Erro ao tentar executar o create table: {e}")


    logging.info(f"Criando registro inicial de controle...")

    # Faz a carga do registro inicial de controle de ingestão

    query = f'''
        INSERT INTO ingest_control (table_ingested, ref_timestamp_column, last_ref_timestamp_ingested, ingest_execution_timestamp)
        VALUES ('clients', 'updatetime', '1970-01-01 00:00:00', null)
    '''

    try:
        
        cursor.execute(query)

    except Exception as e:

        logging.info(f"Erro ao tentar inserir o registro de controle inicial: {e}")


    # Criando a stored procedure de atualização da ingest control

    sql_sp = '''
        CREATE PROCEDURE SP_UPDATE_INGEST_CONTROL
        (
            @table_ing nvarchar(50),
            @last_ref_ts_ing datetime2
        )
        AS
            UPDATE ingest_control SET
                last_ref_timestamp_ingested = @last_ref_ts_ing,
                ingest_execution_timestamp = CURRENT_TIMESTAMP
            WHERE
                table_ingested = @table_ing;
    '''

    try:
        
        cursor.execute(sql_sp)

    except Exception as e:

        logging.info(f"Erro ao criar a stored procedure: {e}")


    cnxn.commit()   # Commitando
    
    cursor.close()
    
    cnxn.close()

    return func.HttpResponse(
            "Base de clientes criada com sucesso!",
             status_code=200
        )



###############################################################
# FUNCAO QUE FAZ A CARGA INICIAL DA BASE DE CLIENTES
###############################################################

@app.route(route="LoadDbCustomer", auth_level=func.AuthLevel.ANONYMOUS)
def LoadDbCustomer(req: func.HttpRequest) -> func.HttpResponse:

    now = datetime.datetime.utcnow()

    logging.info(f"Carregando base de dados de clientes as '{now}'")
        
    try:

        cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};PORT=1433;SERVER='+SERVER+';PORT=1443;DATABASE='+DATABASE+';UID='+USER+';PWD='+ PWD)

    except Exception as e:

        logging.info(f"Erro ao tentar acessar o banco: {e}")

    cursor = cnxn.cursor()

    # Carregando os dados de clientes

    clients_list = [
        {
            "id": "1",
            "name": "Mickey",
            "email": "mickey@email.com",
            "phone": "1155676287",
            "postal_code": "02309-010",
            "doc_number": "2653762897",
            "doc_type": "RG",
            "account_number": "12345",
            "account_type": "corrente",
            "inv_prof_type": "conservador",
            "inv_prof_monthly_income": 50000.00,
            "inv_prof_patrimony": 150000.00,
            "inv_prof_objectives": "viagem"
        },
        {
            "id": "2",
            "name": "Donald",
            "email": "donald@email.com",
            "phone": "2255676287",
            "postal_code": "04854-010",
            "doc_number": "3653762898",
            "doc_type": "RG",
            "account_number": "22345",
            "account_type": "poupanca",
            "inv_prof_type": "arrojado",
            "inv_prof_monthly_income": 40000.00,
            "inv_prof_patrimony": 80000.00,
            "inv_prof_objectives": "aposentadoria"
        },
        {
            "id": "3",
            "name": "Pateta",
            "email": "pateta@email.com",
            "phone": "3355676287",
            "postal_code": "01310-930",
            "doc_number": "4653762899",
            "doc_type": "RG",
            "account_number": "32345",
            "account_type": "salario",
            "inv_prof_type": "moderado",
            "inv_prof_monthly_income": 30000.00,
            "inv_prof_patrimony": 50000.00,
            "inv_prof_objectives": "fundo reserva"
        }
    ]

    for client in clients_list:

        try:

            query = f'''
                INSERT INTO clients (
                    id, 
                    name, 
                    email,
                    phone,
                    postal_code, 
                    doc_number,
                    doc_type,
                    account_number,
                    account_type,
                    inv_prof_type,
                    inv_prof_monthly_income,
                    inv_prof_patrimony,
                    inv_prof_objectives,
                    updatetime
                )
                VALUES (
                    '{client["id"]}', 
                    '{client["name"]}', 
                    '{client["email"]}',
                    '{client["phone"]}',
                    '{client["postal_code"]}',
                    '{client["doc_number"]}',
                    '{client["doc_type"]}',
                    '{client["account_number"]}',
                    '{client["account_type"]}',
                    '{client["inv_prof_type"]}',
                    '{client["inv_prof_monthly_income"]}',
                    '{client["inv_prof_patrimony"]}',
                    '{client["inv_prof_objectives"]}',                    
                    CURRENT_TIMESTAMP
                )
            '''

            cursor.execute(query)

        except Exception as e:

            logging.info(f"Erro ao tentar carregar o registro de cliente: {e}")


    cnxn.commit()   # Commitando
    
    cursor.close()
    
    cnxn.close()

    return func.HttpResponse(
            "Carga de clientes executada com sucesso!",
             status_code=200
        )

import azure.functions as func
import datetime
import json
import logging
import random

import asyncio

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.identity.aio import DefaultAzureCredential

import pyodbc

EVENT_HUB_FULLY_QUALIFIED_NAMESPACE = "evhnmprmsdms810401.servicebus.windows.net"
EVENT_HUB_NAME = "evhorders"

credential = DefaultAzureCredential()

app = func.FunctionApp()
    
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
# FUNCAO DE ENVIO DOS EVENTOS DE ORDERS
###############################################################
async def run():

    producer = EventHubProducerClient(
        fully_qualified_namespace=EVENT_HUB_FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENT_HUB_NAME,
        credential=credential,
    )
    async with producer:
        # Create a batch.
        event_data_batch = await producer.create_batch()

        # Add events to the batch.
        event_data_batch.add(EventData('{"id":"123", "symbol":"SANB11", "clientId":"7", "quantity":4}'))
        event_data_batch.add(EventData('{"id":"124", "symbol":"FRIO3", "clientId":"7", "quantity":2}'))
        event_data_batch.add(EventData('{"id":"125", "symbol":"PETR4", "clientId":"17", "quantity":1}'))
    
        # Send the batch of events to the event hub.
        await producer.send_batch(event_data_batch)

        # Close credential when no longer needed.
        await credential.close()


@app.timer_trigger(schedule="0 */5 * * * *",     # A cada 5 minutos
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
# FUNCAO QUE FAZ A CARGA INICIAL DA BASE DE CLIENTES
###############################################################

# Como invocar:

# curl -k https://afarmsdms810401.azurewebsites.net/api/loaddbcustomer

@app.route(route="LoadDbCustomer", auth_level=func.AuthLevel.ANONYMOUS)
def LoadDbCustomer(req: func.HttpRequest) -> func.HttpResponse:

    now = datetime.datetime.utcnow()

    logging.info(f"Carregando base de dados de clientes as '{now}'")

    SERVER = "sdbrmsdms810401.database.windows.net"
    DATABASE = "CUSTOMER"
    USER = "sqldbrms_usr"
    PWD = f"pwdD8*DMS#"
        
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
            postal_code varchar(15) NOT NULL,
            updatetime datetime NOT NULL
        )
    '''

    control_table = '''
        CREATE TABLE ingest_control (
            table_ingested varchar(50) NOT NULL,
            ref_timestamp_column varchar(50) NOT NULL,
            last_ref_timestamp_ingested datetime NOT NULL,
            ingest_execution_timestamp datetime NOT NULL
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


    # Carregando os dados de clientes

    clients_list = [
        {
            "id": "1",
            "name": "Mickey",
            "postal_code": "02309-010"
        },
        {
            "id": "2",
            "name": "Donald",
            "postal_code": "04854-010"
        },
        {
            "id": "3",
            "name": "Pateta",
            "postal_code": "02309-010"
        }
    ]

    for client in clients_list:

        try:

            query = f'''
                INSERT INTO clients (id, name, postal_code, updatetime)
                VALUES ('{client["id"]}', '{client["name"]}', '{client["postal_code"]}', CURRENT_TIMESTAMP)
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



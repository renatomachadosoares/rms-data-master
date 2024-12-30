import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()

@app.route(route="HttpExample", auth_level=func.AuthLevel.ANONYMOUS)
def HttpExample(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully. Congratulations!")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
    
@app.route(route="StockQuotes", auth_level=func.AuthLevel.ANONYMOUS)
def GetPrices(req: func.HttpRequest) -> func.HttpResponse:

    quotes = [
        {
            "papel": "SANB11",
            "valor": 10000.7,
            "timestamp": "2024-10-10 19:45:56"
        },
        {
            "papel": "PETR4",
            "valor": 500.9,
            "timestamp": "2024-10-10 19:45:56"
        },
        {
            "papel": "PETR7",
            "valor": 510.9,
            "timestamp": "2024-10-10 19:45:57"
        }

    ]

    return func.HttpResponse(
             json.dumps(quotes),
             mimetype="application/json",
             status_code=200
        )


#### FUNCAO COM TIMER, FAZER O DEPLOY SÒ QUANDO NECESSARIO POIS NÂO SEI O CUSTO!
'''
@app.function_name(name="mytimer")
@app.timer_trigger(schedule="* * * * * *", 
              arg_name="mytimer",
              run_on_startup=True) 
def test_function(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s ok!', utc_timestamp)
'''
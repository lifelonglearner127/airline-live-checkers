import azure.functions as func
import json
import logging
from live_checkers.enums import Airline
from live_checkers.aa.scraper import get_flight_points

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="live_checker")
def live_checker(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        payload = req.get_json()
        airline = payload["airline"]
        origin = payload["origin"]
        destination = payload["destination"]
        departure_date = payload["departure_date"]
        departure_time = payload.get("departure_time")
        flight_no = payload.get("flight_no")
        cabin_class = payload.get("cabin_class")
        if airline.lower() == Airline.AmericanAirlines:
            response = get_flight_points(
                origin=origin,
                destination=destination,
                flight_date=departure_date,
                flight_time=departure_time,
                flight_no=flight_no,
                cabin_class=cabin_class,
            )
    except Exception as e:
        logging.error(f"Exception {e}")
    else:
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
        )

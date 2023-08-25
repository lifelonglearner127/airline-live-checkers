import requests
from live_checkers.exceptions import ScrapingException
from live_checkers.enums import Airline
from live_checkers.aa.constants import GET_FLIGHT_POINTS_HEADDER, CABIN_CLASSES


def get_flight_points(
    origin: str,
    destination: str,
    departure_date: str,
    departure_time: str,
    flight_no: str,
    cabin_class: str,
) -> int:
    json_data = {
        "metadata": {
            "selectedProducts": [],
            "tripType": "OneWay",
            "udo": {},
        },
        "passengers": [
            {
                "type": "adult",
                "count": 1,
            },
        ],
        "requestHeader": {
            "clientId": "AAcom",
        },
        "slices": [
            {
                "allCarriers": True,
                "cabin": "",
                "departureDate": departure_date,
                "destination": destination,
                "destinationNearbyAirports": False,
                "maxStops": None,
                "origin": origin,
                "originNearbyAirports": False,
            },
        ],
        "tripOptions": {
            "searchType": "Award",
            "corporateBooking": False,
            "locale": "en_US",
        },
        "loyaltyInfo": None,
        "queryParams": {
            "sliceIndex": 0,
            "sessionId": "",
            "solutionSet": "",
            "solutionId": "",
        },
    }
    try:
        response = requests.post(
            "https://www.aa.com/booking/api/search/itinerary",
            headers=GET_FLIGHT_POINTS_HEADDER,
            json=json_data,
            timeout=30,
        )
        if response.status_code != 200:
            raise ScrapingException(
                airline=Airline.AmericanAirlines.value,
                origin=origin,
                destination=destination,
                date=departure_date,
                data=response.text,
            )
        data = response.json()
        slices = data.get("slices", [])
        for s in slices:
            if departure_time:
                departure_date_time = s.get("departureDateTime", "")
                if departure_time not in departure_date_time:
                    continue

            for slice_segment in s.get("segments", []):
                flight_number = slice_segment.get("flight", {}).get("flightNumber", "")
                if flight_number == flight_no:
                    for cabin_price in s.get("pricingDetail", []):
                        product_type = cabin_price.get("productType", "")
                        if CABIN_CLASSES.get(product_type) == cabin_class:
                            return cabin_price.get("perPassengerAwardPoints", -1)
        else:
            return -1
    except (ScrapingException, Exception) as e:
        raise e

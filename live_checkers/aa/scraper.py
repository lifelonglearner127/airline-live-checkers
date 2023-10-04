import requests
import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional, List
from live_checkers.exceptions import ScrapingException
from live_checkers.enums import Airline
from live_checkers.aa.constants import (
    GET_FLIGHT_POINTS_HEADDER,
    CABIN_CLASSES,
    CABIN_CLASS_MAPPING,
)


@dataclass(frozen=True)
class FlightSegment:
    origin: str
    destination: str
    departure_date: str
    departure_time: str
    departure_timezone: str
    arrival_date: str
    arrival_time: str
    arrival_timezone: str
    flight_number: str
    aircraft: str
    amenities: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class FlightPointInfo:
    origin: str
    destination: str
    cabin_class: str
    airline_cabin_class: str
    duration: int
    stops: int
    departure_date: str
    departure_time: str
    departure_timezone: str
    arrival_date: str
    arrival_time: str
    arrival_timezone: str
    points: float
    cash_fee: Optional[float] = 0
    stop_cities: List[str] = field(default_factory=list)
    carriers: List[str] = field(default_factory=list)
    segments: List[FlightSegment] = field(default_factory=list)


@dataclass(frozen=True)
class FlightTime:
    date: str
    time: str
    timezone: str


def parse_datetime(time_format_string: str) -> FlightTime:
    parsed_datetime = datetime.datetime.strptime(
        time_format_string, "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    return FlightTime(
        date=parsed_datetime.date().isoformat(),
        time=parsed_datetime.time().isoformat(),
        timezone=f"{parsed_datetime.tzinfo}",
    )


# def get_flight_points(
#     origin: str,
#     destination: str,
#     departure_date: str,
#     departure_time: Optional[str] = None,
#     flight_no: Optional[str] = None,
#     cabin_class: Optional[str] = None,
# ) -> int:
def get_flight_points(
    origin: str,
    destination: str,
    flight_date: str,
    flight_time: Optional[str] = None,
    flight_no: Optional[str] = None,
    cabin_class: Optional[str] = None,
) -> List[FlightPointInfo]:
    points: List[FlightPointInfo] = []
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
                "departureDate": flight_date,
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
        )
        if response.status_code != 200:
            raise ScrapingException(
                airline=Airline.AmericanAirlines.value,
                origin=origin,
                destination=destination,
                date=flight_date,
                data=response.text,
            )

        data = response.json()
        if data["error"]:
            raise ScrapingException(
                airline=Airline.AmericanAirlines.value,
                origin=origin,
                destination=destination,
                date=flight_date,
                data=response.text,
            )

        slices = data.get("slices", [])
        for slice in slices:
            flight = {}
            flight["origin"] = slice.get("origin", {}).get("code", "")
            flight["destination"] = slice.get("destination", {}).get("code", "")
            flight["duration"] = slice.get("durationInMinutes", 0)
            flight["stops"] = slice.get("stops", 0)
            departure_date_time = slice.get("departureDateTime", "")
            if departure_date_time:
                parsed_datetime = parse_datetime(departure_date_time)
                flight["departure_date"] = parsed_datetime.date
                flight["departure_time"] = parsed_datetime.time
                flight["departure_timezone"] = parsed_datetime.timezone
            arrival_date_time = slice.get("arrivalDateTime", "")
            if arrival_date_time:
                parsed_datetime = parse_datetime(arrival_date_time)
                flight["arrival_date"] = parsed_datetime.date
                flight["arrival_time"] = parsed_datetime.time
                flight["arrival_timezone"] = parsed_datetime.timezone
            connecting_cities = slice.get("connectingCities", [])
            if connecting_cities:
                flight["stop_cities"] = [
                    connectingCity.get("code", "")
                    for connectingCity in connecting_cities[0]
                    if connectingCity.get("code", "")
                ]
            flight["carriers"] = slice.get("carrierNames", [])
            segments = []
            for slice_segment in slice.get("segments", []):
                segment = dict()
                segment["origin"] = slice_segment.get("origin", {}).get("code", "")
                segment["destination"] = slice_segment.get("destination", {}).get(
                    "code", ""
                )
                segment_departure_date_time = slice_segment.get("departureDateTime", "")
                if segment_departure_date_time:
                    parsed_datetime = parse_datetime(segment_departure_date_time)
                    segment["departure_date"] = parsed_datetime.date
                    segment["departure_time"] = parsed_datetime.time
                    segment["departure_timezone"] = parsed_datetime.timezone
                segment_arrival_date_time = slice_segment.get("arrivalDateTime", "")
                if segment_arrival_date_time:
                    parsed_datetime = parse_datetime(segment_arrival_date_time)
                    segment["arrival_date"] = parsed_datetime.date
                    segment["arrival_time"] = parsed_datetime.time
                    segment["arrival_timezone"] = parsed_datetime.timezone

                segment["flight_number"] = slice_segment.get("flight", {}).get(
                    "flightNumber", ""
                )

                segment_legs = slice_segment.get("legs", [])
                if segment_legs:
                    segment_leg = segment_legs[0]
                    aircraft = [
                        segment_leg.get("aircraft", {}).get("code", ""),
                        segment_leg.get("aircraft", {}).get("shortName", ""),
                    ]
                    segment["aircraft"] = "-".join(
                        [_it.strip() for _it in aircraft if _it.strip()]
                    )
                    segment["amenities"] = segment_leg.get("amenities", [])

                segments.append(segment)
            flight["segments"] = segments

            for cabin_price in slice.get("pricingDetail", []):
                product_type = cabin_price.get("productType", "")
                flight["airline_cabin_class"] = CABIN_CLASSES.get(
                    product_type, product_type
                )
                flight["cabin_class"] = CABIN_CLASS_MAPPING.get(
                    flight["airline_cabin_class"], ""
                )
                if flight["cabin_class"].lower() != cabin_class.lower():
                    continue

                flight["points"] = cabin_price.get("perPassengerAwardPoints", -1)
                if not flight["points"]:
                    flight["points"] = -1
                flight["cash_fee"] = cabin_price.get(
                    "perPassengerTaxesAndFees", {}
                ).get("amount", 0)

                points.append(FlightPointInfo(**flight))

        return [asdict(point) for point in points]
    except (ScrapingException, Exception) as e:
        raise e

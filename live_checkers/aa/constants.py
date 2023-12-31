GET_FLIGHT_POINTS_HEADDER = {
    "authority": "www.aa.com",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.aa.com",
    "referer": "https://www.aa.com/booking/choose-flights/1",
    "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}
CABIN_CLASSES = {
    "COACH": "Main Cabin",
    "PREMIUM_COACH": "Premium Economy",
    "BUSINESS,FIRST": "Business / First",
    "FIRST": "First",
}
CABIN_CLASS_MAPPING = {
    "Main Cabin": "economy",
    "Premium Economy": "premium_economy",
    "Business / First": "business,first",
    "First": "first",
}

from typing import Optional


class ScrapingException(Exception):
    def __init__(
        self,
        airline: str,
        origin: str,
        destination: str,
        date: str,
        data: Optional[str] = None,
        *args,
    ):
        self.message = f"{airline} ({origin} - {destination}) on {date}: {data}"
        super().__init__(self.message, *args)

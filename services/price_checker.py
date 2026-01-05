from datetime import date
from services.yf_service import (
    fetch_current_price_yf,
    fetch_historical_price_yf
)


def fetch_current_price(ticker: str) -> float | None:
    return fetch_current_price_yf(ticker)


def fetch_historical_price(ticker: str, on_date: date) -> float | None:
    return fetch_historical_price_yf(ticker, on_date)

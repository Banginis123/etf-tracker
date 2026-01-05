import yfinance as yf
from datetime import date


def fetch_current_price_yf(ticker: str) -> float | None:
    """
    Grąžina naujausią uždarymo kainą (Close).
    """
    try:
        data = yf.download(
            ticker,
            period="5d",
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            return None

        return data["Close"].iloc[-1].item()

    except Exception as e:
        print(f"Klaida gaunant dabartinę kainą {ticker}: {e}")
        return None


def fetch_historical_price_yf(ticker: str, on_date: date) -> float | None:
    """
    Grąžina Close kainą konkrečiai datai.
    Jei rinka nedirbo – ima paskutinę ankstesnę.
    """
    try:
        data = yf.download(
            ticker,
            end=on_date.isoformat(),
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            return None

        return data["Close"].iloc[-1].item()

    except Exception as e:
        print(f"Klaida gaunant istorinę kainą {ticker}: {e}")
        return None


def get_all_time_high(ticker: str) -> float | None:
    """
    Grąžina visų laikų aukščiausią Close kainą.
    Naudojama ATH cache'ui.
    """
    try:
        data = yf.download(
            ticker,
            period="max",
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            return None

        return data["Close"].max().item()

    except Exception as e:
        print(f"Klaida gaunant ATH {ticker}: {e}")
        return None


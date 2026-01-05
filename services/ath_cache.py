from datetime import datetime, timedelta
from services.yf_service import get_all_time_high
from database import SessionLocal
from models import ETF


def get_or_create_ath(etf: ETF) -> float | None:
    """
    1. Jei ATH jau yra DB – grąžinam
    2. Jei nėra – pasiimam iš Yahoo, išsaugom DB, grąžinam
    """
    if etf.ath_price is not None:
        return etf.ath_price

    ath = get_all_time_high(etf.ticker)
    if ath is None:
        return None

    db = SessionLocal()
    etf.ath_price = ath
    etf.ath_updated_at = datetime.utcnow()
    etf.ath_alert_sent = False
    etf.manual_reset_at = None
    db.merge(etf)
    db.commit()
    db.close()

    print(f"📌 ATH cache sukurtas {etf.ticker}: {ath:.2f}")
    return ath


def update_ath_if_new(etf: ETF, current_price: float) -> bool:
    """
    Jei kaina > ATH → atnaujinam DB.
    Grąžina True jei tai NAUJAS ATH.
    """
    if etf.ath_price is None or current_price > etf.ath_price:
        db = SessionLocal()
        etf.ath_price = current_price
        etf.ath_updated_at = datetime.utcnow()
        etf.ath_alert_sent = False
        etf.manual_reset_at = None
        db.merge(etf)
        db.commit()
        db.close()

        print(f"🚀 Naujas ATH {etf.ticker}: {current_price:.2f}")
        return True

    return False


def calculate_drop_percentage(etf: ETF, current_price: float) -> float | None:
    """
    Skaičiuoja kritimą nuo ATH procentais.
    """
    if not etf.ath_price or etf.ath_price <= 0:
        return None

    drop = ((etf.ath_price - current_price) / etf.ath_price) * 100
    return round(drop, 2)


def is_alert_allowed(etf: ETF) -> bool:
    """
    Alert leidžiamas tik jei:
    - ath_alert_sent == False
    - manual_reset_at nėra arba senesnis nei 24h
    """
    if etf.ath_alert_sent:
        return False

    if etf.manual_reset_at:
        if datetime.utcnow() - etf.manual_reset_at < timedelta(hours=24):
            return False

    return True


def mark_alert_sent(etf: ETF):
    """
    Pažymi, kad alertas buvo išsiųstas.
    """
    db = SessionLocal()
    etf.ath_alert_sent = True
    db.merge(etf)
    db.commit()
    db.close()

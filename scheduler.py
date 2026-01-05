# scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from database import SessionLocal
from models import ETF
from services.price_checker import fetch_current_price
from services.ath_cache import (
    update_ath_if_new,
    get_or_create_ath,
)
from services.alerts import create_alert
from services.email_service import send_daily_summary_if_needed

scheduler = BackgroundScheduler()


def is_alert_allowed(etf: ETF) -> bool:
    """
    Alert leidimo logika:
    - jei alert jau buvo siųstas → blokuojam
    - manual reset leidžia alertą iš karto
    """
    if etf.ath_alert_sent:
        return False

    return True


def calculate_drop_percentage(etf: ETF, current_price: float) -> float | None:
    """
    Kritimo nuo ATH skaičiavimas
    """
    if not etf.ath_price or etf.ath_price <= 0:
        return None

    return ((etf.ath_price - current_price) / etf.ath_price) * 100


def process_single_etf(db, etf, triggered_alerts):
    """
    Apdoroja vieną ETF
    """
    current_price = fetch_current_price(etf.ticker)
    if current_price is None:
        return

    # 0️⃣ Užtikrinam, kad ATH egzistuoja
    ath_price = get_or_create_ath(etf)
    if ath_price is None:
        return

    # 1️⃣ ATH scenarijus
    old_ath = etf.ath_price
    update_ath_if_new(etf, current_price)

    # Jei buvo naujas ATH – resetinam alert būseną
    if etf.ath_price != old_ath:
        etf.ath_alert_sent = 0
        etf.manual_reset_at = None
        db.commit()
        return

    # 2️⃣ Drop scenarijus
    drop_percent = calculate_drop_percentage(etf, current_price)
    if drop_percent is None:
        return

    if drop_percent < etf.drop_threshold:
        return

    # 3️⃣ Alert blokavimas
    if not is_alert_allowed(etf):
        return

    # 4️⃣ Alert sukūrimas
    create_alert(
        etf=etf,
        current_price=current_price,
        drop_percent=drop_percent,
    )

    etf.ath_alert_sent = 1
    db.commit()

    triggered_alerts.append(
        {
            "ticker": etf.ticker,
            "ath": etf.ath_price,
            "price": current_price,
            "drop": drop_percent,
        }
    )


def check_etf_prices():
    """
    Scheduler ciklas
    """
    print(f"⏱️ ETF check started @ {datetime.now()}")

    db = SessionLocal()
    triggered_alerts = []

    try:
        etfs = db.query(ETF).all()
        for etf in etfs:
            process_single_etf(db, etf, triggered_alerts)
    finally:
        db.close()

    send_daily_summary_if_needed(triggered_alerts)
    print(f"✅ ETF check finished @ {datetime.now()}")


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        check_etf_prices,
        trigger=IntervalTrigger(minutes=5),
        id="etf_price_check",
        replace_existing=True,
    )

    scheduler.start()
    print(f"🟢 Scheduler started @ {datetime.now()}")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("🔴 Scheduler stopped")

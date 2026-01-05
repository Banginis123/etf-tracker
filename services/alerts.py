from datetime import datetime
from database import SessionLocal
from models import Alert, ETF
from sqlalchemy import text


def create_alert(etf: ETF, current_price: float, drop_percent: float) -> Alert:
    """
    Sukuria alert DB įrašą (1 alert = 1 ATH ciklas)
    drop_percent NESAUGOMAS DB – naudojamas tik logikai / email
    """
    db = SessionLocal()

    # ⛔ NE naudojam ORM insert, nes DB schema sena
    # ✅ Explicit INSERT tik su egzistuojančiais stulpeliais
    db.execute(
        text(
            """
            INSERT INTO alerts (etf_id, price, created_at)
            VALUES (:etf_id, :price, :created_at)
            """
        ),
        {
            "etf_id": etf.id,
            "price": current_price,
            "created_at": datetime.utcnow(),
        },
    )

    # Pažymim, kad šiam ATH alertas jau išsiųstas
    etf.ath_alert_sent = True
    db.merge(etf)

    db.commit()

    print(
        f"🚨 ALERT sukurtas: {etf.ticker} | "
        f"Kaina: {current_price:.2f} | "
        f"Kritimas: {drop_percent:.2f}%"
    )

    db.close()

    return None

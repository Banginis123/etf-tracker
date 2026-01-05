from fastapi import APIRouter
from database import SessionLocal
from models import ETF

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/etfs")
def list_etfs():
    db = SessionLocal()
    try:
        etfs = db.query(ETF).all()
        return [
            {
                "id": e.id,
                "ticker": e.ticker,
                "ath_price": e.ath_price,
                "ath_alert_sent": e.ath_alert_sent
            }
            for e in etfs
        ]
    finally:
        db.close()

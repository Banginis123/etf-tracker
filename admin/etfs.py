from fastapi import APIRouter
from database import SessionLocal
from models import ETF
from services.yf_service import get_current_price

router = APIRouter(prefix="/admin/etfs", tags=["Admin ETFs"])

@router.get("")
def list_etfs():
    db = SessionLocal()
    try:
        etfs = db.query(ETF).all()
        result = []

        for etf in etfs:
            current_price = get_current_price(etf.ticker)

            result.append({
                "id": etf.id,
                "ticker": etf.ticker,
                "ath_price": etf.ath_price,
                "ath_alert_sent": etf.ath_alert_sent,
                "current_price": current_price
            })

        return result
    finally:
        db.close()

from fastapi import APIRouter, HTTPException
from database import SessionLocal
from models import ETF

router = APIRouter(prefix="/admin", tags=["Admin"])

# 📋 1. Matyti visus ETF
@router.get("/etfs")
def list_etfs():
    db = SessionLocal()
    try:
        etfs = db.query(ETF).all()
        return [
            {
                "id": etf.id,
                "ticker": etf.ticker,
                "ath_price": etf.ath_price,
                "ath_alert_sent": etf.ath_alert_sent
            }
            for etf in etfs
        ]
    finally:
        db.close()


# ✏️ 2. Keisti ath_price arba ath_alert_sent
@router.put("/etfs/{etf_id}")
def update_etf(
    etf_id: int,
    ath_price: float | None = None,
    ath_alert_sent: int | None = None
):
    db = SessionLocal()
    try:
        etf = db.query(ETF).filter(ETF.id == etf_id).first()
        if not etf:
            raise HTTPException(status_code=404, detail="ETF nerastas")

        if ath_price is not None:
            etf.ath_price = ath_price

        if ath_alert_sent is not None:
            etf.ath_alert_sent = ath_alert_sent

        db.commit()
        return {"status": "ok"}
    finally:
        db.close()


# 🔁 3. Rankinis alert reset
@router.post("/etfs/{etf_id}/reset-alert")
def reset_alert(etf_id: int):
    db = SessionLocal()
    try:
        etf = db.query(ETF).filter(ETF.id == etf_id).first()
        if not etf:
            raise HTTPException(status_code=404, detail="ETF nerastas")

        etf.ath_alert_sent = 0
        db.commit()
        return {"status": "alert resetintas"}
    finally:
        db.close()

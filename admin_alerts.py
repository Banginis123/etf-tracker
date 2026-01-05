from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from database import SessionLocal
from models import Alert, ETF
from templating import templates

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/alerts")
def alert_history(request: Request, db: Session = Depends(get_db)):
    # -------------------------
    # Alert history (last 10)
    # -------------------------
    results = (
        db.query(
            Alert.id,
            Alert.price,
            Alert.created_at,
            ETF.ticker,
            ETF.ath_price,
        )
        .join(ETF, Alert.etf_id == ETF.id)
        .order_by(Alert.created_at.desc())
        .limit(10)
        .all()
    )

    alerts = [
        {
            "id": r.id,
            "price": float(r.price),
            "created_at": r.created_at,
            "ticker": r.ticker,
            "ath_price": float(r.ath_price) if r.ath_price is not None else None,
        }
        for r in results
    ]

    # -------------------------
    # Alert settings + last alert price
    # -------------------------
    etfs = db.query(ETF).all()

    last_alerts = (
        db.query(
            Alert.etf_id,
            func.max(Alert.created_at).label("last_time"),
        )
        .group_by(Alert.etf_id)
        .subquery()
    )

    last_prices = (
        db.query(Alert.etf_id, Alert.price)
        .join(
            last_alerts,
            (Alert.etf_id == last_alerts.c.etf_id)
            & (Alert.created_at == last_alerts.c.last_time),
        )
        .all()
    )

    last_price_map = {etf_id: float(price) for etf_id, price in last_prices}

    for etf in etfs:
        etf.last_alert_price = last_price_map.get(etf.id)

    return templates.TemplateResponse(
        "admin/alerts.html",
        {
            "request": request,
            "alerts": alerts,
            "etfs": etfs,
        },
    )


@router.post("/api/etfs/{etf_id}/threshold")
async def update_drop_threshold(
    etf_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    form = await request.form()
    new_threshold = float(form.get("drop_threshold"))

    etf = db.query(ETF).filter(ETF.id == etf_id).first()
    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")

    etf.drop_threshold = new_threshold
    db.commit()

    return RedirectResponse(url="/admin/alerts", status_code=303)


@router.post("/api/etfs/{etf_id}/reset")
def manual_reset(etf_id: int, db: Session = Depends(get_db)):
    etf = db.query(ETF).filter(ETF.id == etf_id).first()

    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")

    # 🔥 Ištrinam visus alertus → last_alert_price tampa None
    db.query(Alert).filter(Alert.etf_id == etf_id).delete()

    etf.manual_reset_at = datetime.utcnow()
    etf.ath_alert_sent = False
    db.commit()

    return RedirectResponse(url="/admin/alerts", status_code=303)

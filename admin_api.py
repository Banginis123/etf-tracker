from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from models import Alert, ETF, Purchase, PortfolioYTD

router = APIRouter(
    prefix="/admin/api",
    tags=["admin-api"],
)

# =========================================================
# DB dependency
# =========================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================================================
# YTD INVALIDATION (CRITICAL)
# =========================================================
def invalidate_current_year_ytd(db: Session):
    current_year = datetime.utcnow().year
    db.query(PortfolioYTD).filter(
        PortfolioYTD.year == current_year
    ).delete()
    db.commit()

# =========================================================
# HELPERS
# =========================================================
def get_units_until(
    db: Session,
    etf_id: int,
    until_dt: datetime,
    exclude_id: int | None = None,
):
    query = db.query(Purchase).filter(
        Purchase.etf_id == etf_id,
        Purchase.purchased_at <= until_dt,
    )

    if exclude_id is not None:
        query = query.filter(Purchase.id != exclude_id)

    return sum(p.units for p in query.all())

# =========================================================
# GET /admin/api/alerts
# =========================================================
@router.get("/alerts")
def get_alert_history(db: Session = Depends(get_db)):
    results = (
        db.query(
            Alert.id,
            ETF.ticker,
            Alert.price,
            ETF.ath_price,
            Alert.created_at,
        )
        .join(ETF, Alert.etf_id == ETF.id)
        .order_by(desc(Alert.created_at))
        .all()
    )

    return [
        {
            "id": r.id,
            "ticker": r.ticker,
            "price": r.price,
            "ath_price": r.ath_price,
            "created_at": r.created_at,
        }
        for r in results
    ]

# =========================================================
# GET /admin/api/etfs
# =========================================================
@router.get("/etfs")
def get_etfs(db: Session = Depends(get_db)):
    etfs = db.query(ETF).all()

    return [
        {
            "id": etf.id,
            "ticker": etf.ticker,
            "ath_price": etf.ath_price,
            "drop_threshold": etf.drop_threshold,
            "ath_alert_sent": etf.ath_alert_sent,
            "manual_reset_at": etf.manual_reset_at,
        }
        for etf in etfs
    ]

# =========================================================
# POST /admin/api/etfs
# =========================================================
@router.post("/etfs")
def create_etf(
    ticker: str = Form(...),
    drop_threshold: float = Form(...),
    db: Session = Depends(get_db),
):
    etf = ETF(
        ticker=ticker.upper(),
        drop_threshold=drop_threshold,
        ath_price=None,
        ath_alert_sent=False,
        manual_reset_at=None,
    )

    try:
        db.add(etf)
        db.commit()
    except IntegrityError:
        db.rollback()
        return RedirectResponse(
            "/admin/etfs/new?error=ETF+with+this+ticker+already+exists",
            status_code=303,
        )

    return RedirectResponse("/admin/etfs", status_code=303)

# =========================================================
# UPDATE ETF
# =========================================================
@router.post("/etfs/{etf_id}")
def update_etf(
    etf_id: int,
    drop_threshold: float = Form(...),
    db: Session = Depends(get_db),
):
    etf = db.query(ETF).filter(ETF.id == etf_id).first()
    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")

    etf.drop_threshold = drop_threshold
    db.commit()

    return RedirectResponse("/admin/etfs", status_code=303)

# =========================================================
# DELETE ETF
# =========================================================
@router.delete("/etfs/{etf_id}")
def delete_etf(etf_id: int, db: Session = Depends(get_db)):
    etf = db.query(ETF).filter(ETF.id == etf_id).first()
    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")

    has_purchases = (
        db.query(Purchase)
        .filter(Purchase.etf_id == etf_id)
        .count() > 0
    )

    if has_purchases:
        raise HTTPException(
            status_code=400,
            detail="ETF cannot be deleted because it has purchases",
        )

    db.query(Alert).filter(Alert.etf_id == etf_id).delete()
    db.delete(etf)
    db.commit()

    return {"status": "deleted", "id": etf_id}

# =========================================================
# PURCHASES (BUY / SELL)
# =========================================================
@router.post("/purchases")
def create_purchase(
    etf_id: int = Form(...),
    side: str = Form(...),           # BUY / SELL
    units: float = Form(...),
    price: float = Form(...),
    purchased_at: str = Form(...),
    currency: str = Form("EUR"),
    comment: str = Form(""),
    db: Session = Depends(get_db),
):
    purchased_dt = datetime.fromisoformat(purchased_at)
    units = abs(units)

    if side == "SELL":
        available = get_units_until(db, etf_id, purchased_dt)
        if units > available:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot sell {units}, only {available} available",
            )
        units = -units

    purchase = Purchase(
        etf_id=etf_id,
        units=units,
        price=price,
        purchased_at=purchased_dt,
        currency=currency.upper(),
        comment=comment,
    )

    db.add(purchase)
    db.commit()
    invalidate_current_year_ytd(db)

    # ✅ FIXED REDIRECT
    return RedirectResponse("/admin", status_code=303)

@router.get("/purchases")
def list_purchases(etf_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Purchase)

    if etf_id is not None:
        query = query.filter(Purchase.etf_id == etf_id)

    purchases = query.order_by(Purchase.id.asc()).all()

    return [
        {
            "id": p.id,
            "etf_id": p.etf_id,
            "units": p.units,
            "price": p.price,
            "purchased_at": p.purchased_at,
            "currency": p.currency,
            "comment": p.comment,
        }
        for p in purchases
    ]

@router.get("/purchases/{purchase_id}")
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    return {
        "id": purchase.id,
        "etf_id": purchase.etf_id,
        "units": purchase.units,
        "price": purchase.price,
        "purchased_at": purchase.purchased_at,
        "currency": purchase.currency,
        "comment": purchase.comment,
    }

@router.post("/purchases/{purchase_id}")
def update_purchase(
    purchase_id: int,
    side: str = Form(...),           # BUY / SELL
    units: float = Form(...),
    price: float = Form(...),
    purchased_at: str = Form(...),
    currency: str = Form("EUR"),
    comment: str = Form(""),
    db: Session = Depends(get_db),
):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    purchased_dt = datetime.fromisoformat(purchased_at)
    units = abs(units)

    if side == "SELL":
        available = get_units_until(
            db,
            purchase.etf_id,
            purchased_dt,
            exclude_id=purchase_id,
        )
        if units > available:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot sell {units}, only {available} available",
            )
        units = -units

    purchase.units = units
    purchase.price = price
    purchase.purchased_at = purchased_dt
    purchase.currency = currency.upper()
    purchase.comment = comment

    db.commit()
    invalidate_current_year_ytd(db)

    # ✅ FIXED REDIRECT
    return RedirectResponse("/admin", status_code=303)

@router.delete("/purchases/{purchase_id}")
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    db.delete(purchase)
    db.commit()
    invalidate_current_year_ytd(db)

    return {"status": "deleted", "id": purchase_id}

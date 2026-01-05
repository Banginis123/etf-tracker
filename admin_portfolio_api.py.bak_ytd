from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal
from models import ETF, Purchase

router = APIRouter(
    prefix="/admin/api/portfolio",
    tags=["admin-portfolio-api"],
)

# =========================================================
# DB dependency (lokalus, kaip admin_api.py)
# =========================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# GET /admin/api/portfolio/etfs
# =========================================================
@router.get("/etfs")
def get_etf_portfolio_summary(db: Session = Depends(get_db)):
    results = (
        db.query(
            ETF.id,
            ETF.ticker,
            func.coalesce(func.sum(Purchase.units * Purchase.price), 0).label("total_value"),
            func.coalesce(func.sum(Purchase.units), 0).label("total_units"),
        )
        .outerjoin(Purchase, Purchase.etf_id == ETF.id)
        .group_by(ETF.id, ETF.ticker)
        .order_by(ETF.ticker)
        .all()
    )

    return [
        {
            "id": r.id,
            "ticker": r.ticker,
            "total_units": float(r.total_units),
            "total_value": float(r.total_value),
        }
        for r in results
    ]

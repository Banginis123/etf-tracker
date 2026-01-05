from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import joinedload

from database import SessionLocal
from models import ETF, Purchase
from services.portfolio_calc import calculate_portfolio

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin")
def admin_dashboard(request: Request):
    db = SessionLocal()

    etfs = db.query(ETF).all()

    # 🔴 SVARBIAUSIA VIETA – joinedload
    purchases = (
        db.query(Purchase)
        .options(joinedload(Purchase.etf))
        .all()
    )

    portfolio = calculate_portfolio(db)

    db.close()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "etfs": etfs,
            "purchases": purchases,
            "portfolio": portfolio
        }
    )

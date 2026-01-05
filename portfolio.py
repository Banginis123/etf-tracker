from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from database import SessionLocal
from services.portfolio_calc import calculate_portfolio

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def portfolio_dashboard(request: Request):
    db = SessionLocal()
    data = calculate_portfolio(db)
    db.close()

    return templates.TemplateResponse(
        "portfolio.html",
        {
            "request": request,
            "portfolio": data["rows"],
            "totals": data["totals"],

            # 👇 YTD perduodam AIŠKIAI
            "ytd_eur": data["totals"]["ytd_eur"],
            "ytd_percent": data["totals"]["ytd_percent"],
        }
    )

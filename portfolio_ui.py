from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ETF
from services.yf_service import get_current_price

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
def portfolio(request: Request, db: Session = Depends(get_db)):
    etfs = db.query(ETF).all()

    labels = []
    values = []
    rows = []

    for etf in etfs:
        price = get_current_price(etf.ticker)
        value = etf.units * price if price and etf.units else 0

        if value > 0:
            labels.append(etf.ticker)
            values.append(round(value, 2))

        rows.append({
            "ticker": etf.ticker,
            "units": etf.units,
            "price": price,
            "value": value
        })

    return templates.TemplateResponse(
        "portfolio.html",
        {
            "request": request,
            "labels": labels,
            "values": values,
            "rows": rows,
            "total": round(sum(values), 2)
        }
    )


from fastapi import APIRouter, Depends
from database import SessionLocal
from models import ETF

router = APIRouter(prefix="/etf")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/add")
def add_etf(ticker: str, alert_drop_percent: float = 10.0, db=Depends(get_db)):
    etf = ETF(ticker=ticker.upper(), alert_drop_percent=alert_drop_percent)
    db.add(etf)
    db.commit()
    return {"message": "ETF added", "ticker": ticker}

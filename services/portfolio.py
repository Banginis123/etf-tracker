# services/portfolio.py

from sqlalchemy.orm import Session
from models import ETF


def load_etf_list(db: Session):
    """
    Grąžina visus ETF su prisegtais purchases
    """
    return db.query(ETF).order_by(ETF.ticker).all()


def calculate_portfolio(etf: ETF, current_price: float | None):
    """
    Apskaičiuoja portfolio reikšmes iš pirkimų
    """

    total_units = 0.0
    total_invested = 0.0

    for p in etf.purchases:
        total_units += p.units
        total_invested += p.units * p.price

    avg_buy_price = (
        total_invested / total_units if total_units > 0 else None
    )

    current_value = (
        total_units * current_price if current_price and total_units > 0 else None
    )

    profit = (
        current_value - total_invested
        if current_value is not None
        else None
    )

    profit_percent = (
        (profit / total_invested) * 100
        if profit is not None and total_invested > 0
        else None
    )

    return {
        "units": round(total_units, 4),
        "invested": round(total_invested, 2),
        "avg_buy_price": round(avg_buy_price, 2) if avg_buy_price else None,
        "current_value": round(current_value, 2) if current_value else None,
        "profit": round(profit, 2) if profit else None,
        "profit_percent": round(profit_percent, 2) if profit_percent else None,
    }

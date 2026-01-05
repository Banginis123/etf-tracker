from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload

from models import ETF, PortfolioYTD


def invalidate_current_year_ytd(db: Session):
    current_year = datetime.utcnow().year
    db.query(PortfolioYTD).filter(
        PortfolioYTD.year == current_year
    ).delete()
    db.commit()


def ensure_portfolio_ytd(db: Session):
    current_year = datetime.utcnow().year
    year_start = date(current_year, 1, 1)

    existing = (
        db.query(PortfolioYTD)
        .filter(PortfolioYTD.year == current_year)
        .first()
    )
    if existing:
        return

    etfs = (
        db.query(ETF)
        .options(joinedload(ETF.purchases))
        .all()
    )

    start_value = 0.0

    from services.price_checker import fetch_historical_price

    for etf in etfs:
        units = sum(
            p.units
            for p in etf.purchases
            if p.purchased_at
            and p.purchased_at.date() < year_start
        )

        if units == 0:
            continue

        price = fetch_historical_price(etf.ticker, year_start)
        if price is None:
            continue

        start_value += units * price

    ytd = PortfolioYTD(
        year=current_year,
        start_value=round(start_value, 2),
    )

    db.add(ytd)
    db.commit()

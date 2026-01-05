from sqlalchemy.orm import Session, joinedload
from datetime import datetime, date

from models import ETF, PortfolioYTD
from services.ytd_service import ensure_portfolio_ytd
from services.price_checker import fetch_current_price


def calculate_portfolio(db: Session):
    ensure_portfolio_ytd(db)

    current_year = datetime.utcnow().year
    year_start = date(current_year, 1, 1)

    etfs = (
        db.query(ETF)
        .options(joinedload(ETF.purchases))
        .all()
    )

    rows = []
    total_current_value = 0.0
    total_invested = 0.0
    cash_flows_ytd = 0.0  # 👈 SVARBIAUSIA DALIS

    for etf in etfs:
        units = sum(p.units for p in etf.purchases)
        invested = sum(p.units * p.price for p in etf.purchases)

        if units == 0:
            continue

        current_price = fetch_current_price(etf.ticker) or 0.0
        current_value = units * current_price

        total_current_value += current_value
        total_invested += invested

        # 👇 PINIGŲ SRAUTAI EINAMAIS METAIS
        cash_flows_ytd += sum(
            p.units * p.price
            for p in etf.purchases
            if p.purchased_at
            and p.purchased_at.date() >= year_start
        )

        rows.append({
            "ticker": etf.ticker,
            "units": round(units, 4),
            "avg_buy": round(invested / units, 2),
            "invested": round(invested, 2),
            "current_price": round(current_price, 2),
            "current_value": round(current_value, 2),
        })

    for row in rows:
        invested = row["invested"]
        current_value = row["current_value"]

        pl_eur = current_value - invested
        pl_percent = (pl_eur / invested * 100) if invested > 0 else 0.0

        allocation = (
            current_value / total_current_value * 100
            if total_current_value > 0 else 0.0
        )

        row.update({
            "pl_eur": round(pl_eur, 2),
            "pl_percent": round(pl_percent, 2),
            "allocation": round(allocation, 2),
        })

    ytd_row = (
        db.query(PortfolioYTD)
        .filter(PortfolioYTD.year == current_year)
        .first()
    )

    start_value = ytd_row.start_value if ytd_row else 0.0

    ytd_eur = total_current_value - start_value - cash_flows_ytd
    ytd_percent = (
        (ytd_eur / start_value) * 100
        if start_value > 0 else 0.0
    )

    return {
        "rows": rows,
        "totals": {
            "invested": round(total_invested, 2),
            "current_value": round(total_current_value, 2),
            "pl_eur": round(total_current_value - total_invested, 2),
            "pl_percent": round(
                ((total_current_value - total_invested) / total_invested * 100)
                if total_invested > 0 else 0.0,
                2
            ),
            "ytd_eur": round(ytd_eur, 2),
            "ytd_percent": round(ytd_percent, 2),
        }
    }

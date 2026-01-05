from database import SessionLocal
from models import ETF

db = SessionLocal()

tickers = ["VOO", "SPPE.DE", "EHDV.DE"]

for ticker in tickers:
    exists = db.query(ETF).filter(ETF.ticker == ticker).first()
    if exists:
        print(f"⏭️ {ticker} jau egzistuoja – praleidžiam")
        continue

    etf = ETF(ticker=ticker)
    db.add(etf)
    print(f"✅ Pridėtas {ticker}")

db.commit()
db.close()

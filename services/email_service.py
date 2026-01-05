from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os
from pathlib import Path
import asyncio


# --- ENV ---
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")

if not SMTP_USER or not SMTP_PASS or not ALERT_EMAIL:
    raise ValueError("❌ EMAIL ENV klaida: patikrinkite .env failą!")

# --- MAIL CONFIG ---
conf = ConnectionConfig(
    MAIL_USERNAME=SMTP_USER,
    MAIL_PASSWORD=SMTP_PASS,
    MAIL_FROM=SMTP_USER,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

# --- ASYNC ---
async def send_alert_email(ticker: str, ath: float, current: float, drop_percent: float):
    fm = FastMail(conf)

    subject = f"📉 ETF įspėjimas: {ticker}"

    body = f"""
🟢 ETF TRACKER

ETF: {ticker}
ATH: {ath:.2f}
Dabartinė kaina: {current:.2f}
Kritimas nuo ATH: {drop_percent:.2f}%

---
Automatinis pranešimas
"""

    message = MessageSchema(
        subject=subject,
        recipients=[ALERT_EMAIL],
        body=body,
        subtype="plain",
    )

    await fm.send_message(message)


# --- SYNC WRavoid asyncio scheduler konfliktų ---
def send_alert_email_sync(triggered_etfs):
    fm = FastMail(conf)

    subject = "📉 ETF kritimo įspėjimas"
    body = "Žemiau pateikti ETF nukrito nuo ATH:\n\n"

    for etf in triggered_etfs:
        body += (
            f"ETF: {etf['ticker']}\n"
            f"ATH: {etf['ath']:.2f} Eur\n"
            f"Dabartinė kaina: {etf['price']:.2f} Eur\n"
            f"Kritimas: {etf['drop']:.2f}%\n"
            f"{'-'*25}\n"
        )

    message = MessageSchema(
        subject=subject,
        recipients=[ALERT_EMAIL],
        body=body,
        subtype="plain",
    )

    asyncio.run(fm.send_message(message))


def send_daily_summary_if_needed(triggered_etfs):
    if not triggered_etfs:
        print("📭 Nėra ETF kritusių žemiau ribos – email nesiunčiamas")
        return

    subject = "📉 Dienos ETF kritimo ataskaita"
    body = "Šie ETF nukrito nuo ATH daugiau nei nustatyta riba:\n\n"

    for etf in triggered_etfs:
        body += (
            f"ETF: {etf['ticker']}\n"
            f"ATH: {etf['ath']:.2f}\n"
            f"Dabartinė kaina: {etf['price']:.2f}\n"
            f"Kritimas: {etf['drop']:.2f}%\n"
            f"{'-'*30}\n"
        )

    fm = FastMail(conf)
    message = MessageSchema(
        subject=subject,
        recipients=[ALERT_EMAIL],
        body=body,
        subtype="plain",
    )

    import asyncio
    asyncio.run(fm.send_message(message))

import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

def send_alert_email(ticker, ath, current):
    msg = MIMEText(
        f"ETF: {ticker}\nATH: {ath}\nDabartinė kaina: {current}\n"
        f"Kritimas: {round((1 - current / ath) * 100, 2)} %"
    )
    msg["Subject"] = f"⚠ ETF {ticker} krito nuo ATH"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())

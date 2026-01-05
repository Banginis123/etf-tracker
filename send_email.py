import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

def send_email(subject: str, body: str):
    load_dotenv()

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = os.getenv("EMAIL_RECEIVER")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("Email išsiųstas sėkmingai.")
    except Exception as e:
        print("Klaida siunčiant email:", e)

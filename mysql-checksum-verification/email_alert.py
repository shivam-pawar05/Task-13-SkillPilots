import smtplib
from email.message import EmailMessage
from config import SMTP_CONFIG

def send_alert(subject, body):
    cfg = SMTP_CONFIG
    required = ("host", "username", "password", "sender", "recipient")
    missing = [key for key in required if not cfg.get(key)]
    if missing: raise ValueError("Missing SMTP settings: " + ", ".join(missing))
    message = EmailMessage(); message["Subject"] = subject; message["From"] = cfg["sender"]; message["To"] = cfg["recipient"]; message.set_content(body)
    with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as server:
        server.ehlo(); server.starttls(); server.ehlo(); server.login(cfg["username"], cfg["password"]); server.send_message(message)

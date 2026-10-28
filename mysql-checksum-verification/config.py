import os
from dotenv import load_dotenv
load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "username": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "checksum_demo"),
}
TABLES = [x.strip() for x in os.getenv("CHECKSUM_TABLES", "students,products").split(",") if x.strip()]
SMTP_CONFIG = {"host": os.getenv("SMTP_HOST", ""), "port": int(os.getenv("SMTP_PORT", "587")), "username": os.getenv("SMTP_USERNAME", ""), "password": os.getenv("SMTP_PASSWORD", ""), "sender": os.getenv("SMTP_FROM", ""), "recipient": os.getenv("SMTP_TO", "")}

import argparse, logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from config import DB_CONFIG, TABLES
from checksum import calculate_checksum
from email_alert import send_alert
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"; LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(filename=LOG_DIR / "checksum.log", level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def create_engine_connection():
    url = URL.create("mysql+pymysql", username=DB_CONFIG["username"], password=DB_CONFIG["password"], host=DB_CONFIG["host"], port=DB_CONFIG["port"], database=DB_CONFIG["database"])
    return create_engine(url, pool_pre_ping=True)

def verify_tables(engine, initialize=False):
    mismatches=[]; results=[]
    for table_name in TABLES:
        try:
            current_hash, current_count = calculate_checksum(engine, table_name)
            if initialize:
                with engine.begin() as conn:
                    conn.execute(text("""INSERT INTO table_checksums (table_name, checksum_value, row_count) VALUES (:table_name, :checksum, :row_count) ON DUPLICATE KEY UPDATE checksum_value=VALUES(checksum_value), row_count=VALUES(row_count)"""), {"table_name":table_name,"checksum":current_hash,"row_count":current_count})
                msg=f"BASELINE CREATED | {table_name} | rows={current_count}"; logging.info(msg); results.append(msg); continue
            with engine.connect() as conn:
                stored=conn.execute(text("SELECT checksum_value, row_count FROM table_checksums WHERE table_name=:table_name"), {"table_name":table_name}).mappings().first()
            if stored is None: status="NO_BASELINE"; old_hash=None; old_count=None
            else:
                old_hash=stored["checksum_value"]; old_count=stored["row_count"]
                status="MATCH" if old_hash==current_hash and old_count==current_count else "MISMATCH"
            with engine.begin() as conn:
                conn.execute(text("""INSERT INTO checksum_audit (table_name, stored_checksum, calculated_checksum, stored_rows, calculated_rows, status) VALUES (:table_name,:old_hash,:new_hash,:old_count,:new_count,:status)"""), {"table_name":table_name,"old_hash":old_hash,"new_hash":current_hash,"old_count":old_count,"new_count":current_count,"status":status})
            msg=f"{status} | {table_name} | stored_rows={old_count} | current_rows={current_count}"; logging.info(msg); results.append(msg)
            if status != "MATCH": mismatches.append(msg)
        except Exception as exc:
            msg=f"ERROR | {table_name} | {exc}"; logging.exception(msg); results.append(msg); mismatches.append(msg)
    print("\n".join(results))
    if not initialize and mismatches:
        body="MySQL checksum verification detected differences or errors.\n\n"+"\n".join(mismatches)+"\n\nComplete results:\n"+"\n".join(results)
        try: send_alert("ALERT: MySQL Checksum Verification", body); logging.info("Alert email sent.")
        except Exception: logging.exception("Failed to send alert email."); raise

def main():
    parser=argparse.ArgumentParser(description="Verify MySQL table checksums.")
    parser.add_argument("--initialize-baseline", action="store_true", help="Save current checksums as trusted reference values")
    args=parser.parse_args(); engine=create_engine_connection()
    try: verify_tables(engine, initialize=args.initialize_baseline)
    finally: engine.dispose()
if __name__ == "__main__": main()

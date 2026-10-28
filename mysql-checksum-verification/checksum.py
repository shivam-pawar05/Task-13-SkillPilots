import hashlib, json
from datetime import date, datetime, time
from decimal import Decimal
from sqlalchemy import MetaData, Table, select

def json_default(value):
    if isinstance(value, Decimal): return str(value)
    if isinstance(value, (datetime, date, time)): return value.isoformat()
    if isinstance(value, bytes): return {"bytes_hex": value.hex()}
    raise TypeError(f"Unsupported data type: {type(value).__name__}")

def calculate_checksum(engine, table_name):
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    keys = list(table.primary_key.columns)
    if not keys: raise ValueError(f"Table {table_name} needs a primary key")
    digest = hashlib.sha256(); count = 0
    with engine.connect() as connection:
        for row in connection.execute(select(table).order_by(*keys)):
            encoded = json.dumps(dict(row._mapping), sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=json_default).encode("utf-8")
            digest.update(len(encoded).to_bytes(8, "big")); digest.update(encoded); count += 1
    return digest.hexdigest(), count

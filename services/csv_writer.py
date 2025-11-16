# services/csv_writer.py
import csv
import os
from config.config import REAL_CSV_PATH

def ensure_csv_exists():
    """
    Ensure REAL_CSV_PATH exists with header. If not, create with header row.
    """
    header = ["order_id","timestamp","item","category","quantity","price_per_item","total_amount"]
    dirpath = os.path.dirname(REAL_CSV_PATH)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    if not os.path.exists(REAL_CSV_PATH) or os.path.getsize(REAL_CSV_PATH) == 0:
        with open(REAL_CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)

def write_order_to_csv(order_row: list):
    """
    Append a single order row (list) to REAL_CSV_PATH.
    order_row must be ordered as in header.
    """
    ensure_csv_exists()
    with open(REAL_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(order_row)

# services/csv_loader.py
import pandas as pd
from config.config import REAL_CSV_PATH

def load_csv_orders():
    """
    Load real orders CSV (production). Return pandas DataFrame.
    """
    try:
        df = pd.read_csv(REAL_CSV_PATH)
        return df
    except Exception as e:
        # If file doesn't exist or is empty, return empty DataFrame
        print(f"[csv_loader] Failed to load {REAL_CSV_PATH}: {e}")
        return pd.DataFrame()

# services/dummy_loader.py
import pandas as pd
from config.config import DUMMY_CSV_PATH

def load_dummy_orders():
    """
    Load demo (dummy) CSV. Return pandas DataFrame.
    """
    try:
        df = pd.read_csv(DUMMY_CSV_PATH)
        return df
    except Exception as e:
        print(f"[dummy_loader] Failed to load {DUMMY_CSV_PATH}: {e}")
        return pd.DataFrame()

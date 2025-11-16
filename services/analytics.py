# services/analytics.py
import pandas as pd
from config.config import MODE
from services.dummy_loader import load_dummy_orders
from services.csv_loader import load_csv_orders

def get_orders_df():
    """
    Returns a pandas DataFrame with orders depending on MODE.
    """
    if MODE == "demo":
        return load_dummy_orders()
    return load_csv_orders()

def top_items(limit=10):
    df = get_orders_df()
    if df.empty:
        return []
    # Ensure quantity numeric
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    result = df.groupby("item")["quantity"].sum().sort_values(ascending=False).head(limit)
    return [{"item": i, "quantity": int(q)} for i, q in result.items()]

def peak_hours():
    df = get_orders_df()
    if df.empty:
        return []
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    result = df.groupby("hour").size().reset_index(name="order_count").sort_values("hour")
    return result.to_dict(orient="records")

def weekend_vs_weekday():
    df = get_orders_df()
    if df.empty:
        return {"weekday_orders": 0, "weekend_orders": 0}
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["weekday"] = df["timestamp"].dt.weekday
    weekday_count = int(len(df[df["weekday"] < 5]))
    weekend_count = int(len(df[df["weekday"] >= 5]))
    return {"weekday_orders": weekday_count, "weekend_orders": weekend_count}

def category_sales():
    df = get_orders_df()
    if df.empty:
        return []
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    result = df.groupby("category")["quantity"].sum().reset_index()
    # convert to plain Python types
    return result.to_dict(orient="records")

def revenue_per_day():
    df = get_orders_df()
    if df.empty:
        return []
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["date"] = df["timestamp"].dt.date
    # ensure total_amount numeric
    if "total_amount" in df.columns:
        df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
    result = df.groupby("date")["total_amount"].sum().reset_index()
    result["date"] = result["date"].astype(str)
    return result.to_dict(orient="records")

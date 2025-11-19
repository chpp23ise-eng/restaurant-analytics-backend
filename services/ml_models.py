# services/ml_models.py

import pandas as pd
import numpy as np
from datetime import timedelta
from services.csv_loader import load_csv_orders


# ---------------- Utility Functions ---------------- #

def ensure_timestamp(df):
    """
    Ensure timestamp column exists and is valid.
    """
    df = df.copy()
    if "timestamp" not in df.columns:
        return pd.DataFrame()  # fail-safe

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    return df


def aggregate_daily(df):
    """
    Aggregate total quantity per date for daily trend forecasting.
    """
    df = ensure_timestamp(df)

    if df.empty:
        return pd.DataFrame(columns=["date", "quantity"])

    df["date"] = df["timestamp"].dt.date
    daily = df.groupby("date")["quantity"].sum().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date")
    return daily


# ---------------- Simple Linear Regression (NumPy) ---------------- #

def simple_linear_regression(x, y):
    """
    Returns slope and intercept using normal equation:
        theta = (X^T X)^(-1) X^T y
    """
    x = np.array(x)
    y = np.array(y)

    X = np.column_stack([np.ones(len(x)), x])  # column of ones + x-values
    theta = np.linalg.pinv(X.T @ X) @ X.T @ y

    intercept = theta[0]
    slope = theta[1]
    return slope, intercept


# ---------------- 1️⃣ Predict Tomorrow's Total Orders ---------------- #

def predict_tomorrow(df):
    daily = aggregate_daily(df)

    if daily.empty:
        return {"predicted_orders": 0, "method": "no_data"}

    if len(daily) < 3:
        # Not enough data → fallback to last known value
        return {
            "predicted_orders": int(daily["quantity"].iloc[-1]),
            "method": "fallback_last_value"
        }

    x = daily["date"].map(lambda d: d.toordinal()).values
    y = daily["quantity"].values

    slope, intercept = simple_linear_regression(x, y)

    tomorrow_ord = (daily["date"].iloc[-1] + timedelta(days=1)).toordinal()
    prediction = slope * tomorrow_ord + intercept

    return {
        "predicted_orders": max(0, int(prediction)),
        "method": "numpy_regression"
    }


# ---------------- 2️⃣ Predict Demand for Each Item ---------------- #

def predict_item_demand(df, n_days=7):
    df = ensure_timestamp(df)

    if df.empty:
        return {"results": []}

    df["date"] = df["timestamp"].dt.date
    df["date"] = pd.to_datetime(df["date"])

    grouped = df.groupby(["item", "date"])["quantity"].sum().reset_index()
    items = grouped["item"].unique()

    results = []

    for item in items:
        dfi = grouped[grouped["item"] == item]

        if len(dfi) < 3:
            avg = int(dfi["quantity"].mean()) if len(dfi) > 0 else 0
            results.append({
                "item": item,
                "predictions": [avg] * n_days,
                "method": "fallback_average"
            })
            continue

        x = dfi["date"].map(lambda d: d.toordinal()).values
        y = dfi["quantity"].values

        slope, intercept = simple_linear_regression(x, y)

        last_day = dfi["date"].max()
        preds = []

        for i in range(1, n_days + 1):
            day_ord = (last_day + timedelta(days=i)).toordinal()
            p = slope * day_ord + intercept
            preds.append(max(0, int(p)))

        results.append({
            "item": item,
            "predictions": preds,
            "method": "numpy_regression"
        })

    return {"results": results}


# ---------------- 3️⃣ Predict Peak Hour ---------------- #

def predict_peak_hour(df):
    df = ensure_timestamp(df)

    if df.empty:
        return {"peak_hour": None, "estimate": 0}

    df["hour"] = df["timestamp"].dt.hour

    grouped = df.groupby("hour")["quantity"].sum().reset_index()
    grouped = grouped.sort_values("quantity", ascending=False)

    top = grouped.iloc[0]

    return {
        "peak_hour": int(top["hour"]),
        "estimate": int(top["quantity"]),
        "method": "hourly_grouping"
    }


# ---------------- 4️⃣ Sales Trend ---------------- #

def sales_trend(df):
    daily = aggregate_daily(df)

    if daily.empty or len(daily) < 3:
        return {"trend": "not_enough_data", "slope": 0}

    x = daily["date"].map(lambda d: d.toordinal()).values
    y = daily["quantity"].values

    slope, intercept = simple_linear_regression(x, y)

    if slope > 0:
        t = "increasing"
    elif slope < 0:
        t = "decreasing"
    else:
        t = "stable"

    return {"trend": t, "slope": float(slope)}

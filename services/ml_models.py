# services/ml_models.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from services.csv_loader import load_real_data, load_dummy_data


# ------------ Utility ------------ #

def ensure_timestamp(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    return df


def aggregate_daily(df):
    df = ensure_timestamp(df)
    df["date"] = df["timestamp"].dt.date
    daily = df.groupby("date")["quantity"].sum().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date")
    return daily


# ------------ Simple Linear Regression Using NumPy ------------ #

def simple_linear_regression(x, y):
    """
    Returns slope and intercept using normal equation.
    """
    x = np.array(x)
    y = np.array(y)

    X = np.column_stack([np.ones(len(x)), x])   # [1, x]
    # theta = (X^T X)^(-1) X^T y
    theta = np.linalg.pinv(X.T @ X) @ X.T @ y

    intercept = theta[0]
    slope = theta[1]
    return slope, intercept


# ------------ 1) Predict Tomorrow ------------ #

def predict_tomorrow(df):
    daily = aggregate_daily(df)

    if len(daily) < 3:
        if len(daily) == 0:
            return {"predicted_orders": 0, "method": "no_data"}
        return {"predicted_orders": int(daily['quantity'].iloc[-1]), "method": "last_value"}

    x = daily["date"].map(lambda d: d.toordinal()).values
    y = daily["quantity"].values

    slope, intercept = simple_linear_regression(x, y)

    tomorrow_ord = (daily["date"].iloc[-1] + pd.Timedelta(days=1)).toordinal()
    prediction = slope * tomorrow_ord + intercept

    return {"predicted_orders": max(0, int(prediction)), "method": "numpy_regression"}


# ------------ 2) Predict Item Demand ------------ #

def predict_item_demand(df, n_days=7):
    df = ensure_timestamp(df)
    df["date"] = df["timestamp"].dt.date

    grouped = df.groupby(["item", "date"])["quantity"].sum().reset_index()
    grouped["date"] = pd.to_datetime(grouped["date"])

    items = grouped["item"].unique()
    results = []

    for item in items:
        dfi = grouped[grouped["item"] == item]

        if len(dfi) < 3:
            avg = int(dfi["quantity"].mean()) if len(dfi) > 0 else 0
            results.append({"item": item, "predictions": [avg]*n_days, "method": "average"})
            continue

        x = dfi["date"].map(lambda d: d.toordinal()).values
        y = dfi["quantity"].values

        slope, intercept = simple_linear_regression(x, y)

        last_day = dfi["date"].max()
        preds = []
        for i in range(1, n_days+1):
            day_ord = (last_day + pd.Timedelta(days=i)).toordinal()
            preds.append(max(0, int(slope * day_ord + intercept)))

        results.append({"item": item, "predictions": preds, "method": "numpy_regression"})

    return {"results": results}


# ------------ 3) Peak Hour ------------ #

def predict_peak_hour(df):
    df = ensure_timestamp(df)
    if df.empty:
        return {"peak_hour": None, "estimate": 0}

    df["hour"] = df["timestamp"].dt.hour
    hourly = df.groupby("hour")["quantity"].sum().reset_index()
    hourly = hourly.sort_values("quantity", ascending=False)

    top = hourly.iloc[0]
    return {
        "peak_hour": int(top["hour"]),
        "estimate": int(top["quantity"]),
        "method": "simple_grouping"
    }


# ------------ 4) Trend ------------ #

def sales_trend(df):
    daily = aggregate_daily(df)

    if len(daily) < 3:
        return {"trend": "not_enough_data", "slope": 0}

    x = daily["date"].map(lambda d: d.toordinal()).values
    y = daily["quantity"].values

    slope, intercept = simple_linear_regression(x, y)

    if slope > 0:
        trend = "increasing"
    elif slope < 0:
        trend = "decreasing"
    else:
        trend = "stable"

    return {"trend": trend, "slope": float(slope)}

# services/ml_models.py

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from services.load_csv import load_real_data, load_dummy_data   # <-- adjust if your loader filename differs


# ---------------- Utility ---------------- #

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


# ---------------- 1️⃣ Predict Tomorrow's Orders ---------------- #

def predict_tomorrow(df):
    daily = aggregate_daily(df)

    if len(daily) < 3:
        # fallback
        if len(daily) == 0:
            return {"predicted_orders": 0, "method": "no_data"}
        return {"predicted_orders": int(daily["quantity"].iloc[-1]), "method": "fallback_last_value"}

    daily["ord"] = daily["date"].map(lambda d: d.toordinal())
    X = daily[["ord"]].values
    y = daily["quantity"].values

    model = LinearRegression()
    model.fit(X, y)

    tomorrow_ord = (daily["date"].iloc[-1] + pd.Timedelta(days=1)).toordinal()
    pred = model.predict(np.array([[tomorrow_ord]]))[0]

    return {"predicted_orders": max(0, int(pred)), "method": "linear_regression"}


# ---------------- 2️⃣ Predict Demand Per Item (7 Days Default) ---------------- #

def predict_item_demand(df, n_days=7):
    df = ensure_timestamp(df)
    df["date"] = df["timestamp"].dt.date

    grouped = df.groupby(["item", "date"])["quantity"].sum().reset_index()
    grouped["date"] = pd.to_datetime(grouped["date"])

    items = grouped["item"].unique()

    results = []

    for item in items:
        dfi = grouped[grouped["item"] == item].copy()

        if len(dfi) < 3:
            # fallback: simple average prediction
            avg_val = int(dfi["quantity"].mean()) if len(dfi) > 0 else 0
            results.append({
                "item": item,
                "predictions": [avg_val] * n_days,
                "method": "fallback_average"
            })
            continue

        dfi["ord"] = dfi["date"].map(lambda d: d.toordinal())

        X = dfi[["ord"]].values
        y = dfi["quantity"].values

        model = LinearRegression()
        model.fit(X, y)

        last_dt = dfi["date"].max()

        preds = []
        for i in range(1, n_days + 1):
            future_ord = (last_dt + pd.Timedelta(days=i)).toordinal()
            preds.append(max(0, int(model.predict([[future_ord]])[0])))

        results.append({
            "item": item,
            "predictions": preds,
            "method": "linear_regression"
        })

    return {"results": results}


# ---------------- 3️⃣ Predict Tomorrow's Peak Hour ---------------- #

def predict_peak_hour(df):
    df = ensure_timestamp(df)
    if df.empty:
        return {"peak_hour": None, "estimate": 0, "method": "no_data"}

    df["hour"] = df["timestamp"].dt.hour
    hourly = df.groupby("hour")["quantity"].sum().reset_index()

    hourly = hourly.sort_values("quantity", ascending=False)

    if hourly.empty:
        return {"peak_hour": None, "estimate": 0}

    top = hourly.iloc[0]
    return {
        "peak_hour": int(top["hour"]),
        "estimate": int(top["quantity"]),
        "method": "hourly_grouping"
    }


# ---------------- 4️⃣ Sales Trend Analysis ---------------- #

def sales_trend(df):
    daily = aggregate_daily(df)

    if len(daily) < 3:
        return {"trend": "not_enough_data", "slope": 0}

    daily["ord"] = daily["date"].map(lambda d: d.toordinal())

    X = daily[["ord"]].values
    y = daily["quantity"].values

    model = LinearRegression()
    model.fit(X, y)

    slope = float(model.coef_[0])

    trend = "increasing" if slope > 0 else ("decreasing" if slope < 0 else "stable")

    return {"trend": trend, "slope": slope}

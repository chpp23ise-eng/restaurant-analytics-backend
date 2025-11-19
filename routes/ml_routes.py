# routes/ml_routes.py

from fastapi import APIRouter, Query
from services.csv_loader import load_csv_orders   # ✔ Correct loader
from services.ml_models import (
    predict_tomorrow,
    predict_item_demand,
    predict_peak_hour,
    sales_trend
)

router = APIRouter(tags=["ML"], prefix="/ml")

# No mode handling needed (you only have real CSV)
# --------------------------------------------------

@router.get("/predict-tomorrow")
def ml_predict_tomorrow():
    df = load_csv_orders()
    return predict_tomorrow(df)

@router.get("/predict-item-demand")
def ml_predict_item_demand(n_days: int = Query(7, ge=1, le=30)):
    df = load_csv_orders()
    return predict_item_demand(df, n_days)

@router.get("/predict-peak-hour")
def ml_predict_peak_hour():
    df = load_csv_orders()
    return predict_peak_hour(df)

@router.get("/sales-trend")
def ml_sales_trend():
    df = load_csv_orders()
    return sales_trend(df)

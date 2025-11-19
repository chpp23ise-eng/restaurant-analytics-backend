# routes/ml_routes.py

from fastapi import APIRouter, Query
from config.config import MODE
from services.csv_loader import load_real_data, load_dummy_data   # FIXED LINE

from services.ml_models import (
    predict_tomorrow,
    predict_item_demand,
    predict_peak_hour,
    sales_trend
)

router = APIRouter(tags=["ML"], prefix="/ml")

def resolve_mode(mode_query: str | None):
    if mode_query in ["demo", "production"]:
        return mode_query
    return MODE


@router.get("/predict-tomorrow")
def ml_predict_tomorrow(mode: str | None = Query(None)):
    mode_res = resolve_mode(mode)
    df = load_dummy_data() if mode_res == "demo" else load_real_data()
    return predict_tomorrow(df)


@router.get("/predict-item-demand")
def ml_predict_item_demand(
    mode: str | None = Query(None),
    n_days: int = Query(7, ge=1, le=30)
):
    mode_res = resolve_mode(mode)
    df = load_dummy_data() if mode_res == "demo" else load_real_data()
    return predict_item_demand(df, n_days)


@router.get("/predict-peak-hour")
def ml_predict_peak_hour(mode: str | None = Query(None)):
    mode_res = resolve_mode(mode)
    df = load_dummy_data() if mode_res == "demo" else load_real_data()
    return predict_peak_hour(df)


@router.get("/sales-trend")
def ml_sales_trend(mode: str | None = Query(None)):
    mode_res = resolve_mode(mode)
    df = load_dummy_data() if mode_res == "demo" else load_real_data()
    return sales_trend(df)

# routes/analytics_routes.py
from fastapi import APIRouter
from services.analytics import top_items, peak_hours, weekend_vs_weekday, category_sales, revenue_per_day

router = APIRouter()

@router.get("/top-items")
def _top_items(limit: int = 10):
    return top_items(limit=limit)

@router.get("/peak-hours")
def _peak_hours():
    return peak_hours()

@router.get("/weekend-vs-weekday")
def _weekend_vs_weekday():
    return weekend_vs_weekday()

@router.get("/category-sales")
def _category_sales():
    return category_sales()

@router.get("/revenue-per-day")
def _revenue_per_day():
    return revenue_per_day()

# routes/order_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.config import MODE
from services.csv_writer import write_order_to_csv

router = APIRouter()

class OrderIn(BaseModel):
    order_id: str
    timestamp: str  # "YYYY-MM-DD HH:MM:SS"
    item: str
    category: str
    quantity: int
    price_per_item: float
    total_amount: float

@router.post("/add-order")
def add_order(order: OrderIn):
    """
    Add an order. In demo mode, we do not persist to real CSV.
    In production mode, append to CSV.
    """
    if MODE == "demo":
        return {"status": "demo_mode", "saved": False}

    try:
        row = [
            order.order_id,
            order.timestamp,
            order.item,
            order.category,
            order.quantity,
            order.price_per_item,
            order.total_amount
        ]
        write_order_to_csv(row)
        return {"status": "success", "saved": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save order: {e}")

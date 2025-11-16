# main.py
from fastapi import FastAPI
from routes.analytics_routes import router as analytics_router
from routes.order_routes import router as order_router
from config.config import MODE

app = FastAPI(title="Restaurant Analytics API")

@app.get("/")
def root():
    return {"message": "Restaurant Analytics API", "mode": MODE}

app.include_router(analytics_router, prefix="/analytics")
app.include_router(order_router, prefix="/orders")

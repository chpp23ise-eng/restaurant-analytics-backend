# main.py
from fastapi import FastAPI
from routes.analytics_routes import router as analytics_router
from routes.order_routes import router as order_router
from config.config import MODE
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os


app = FastAPI(title="Restaurant Analytics API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all websites to access API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Restaurant Analytics API", "mode": MODE}

app.include_router(analytics_router, prefix="/analytics")
app.include_router(order_router, prefix="/orders")


DATA_PATH = "data/orders.csv"

@app.get("/download/orders")
def download_orders():
    if os.path.exists(DATA_PATH):
        return FileResponse(
            DATA_PATH,
            media_type="text/csv",
            filename="orders.csv"
        )
    return {"error": "orders.csv not found on server"}

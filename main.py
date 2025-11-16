# main.py
from fastapi import FastAPI
from routes.analytics_routes import router as analytics_router
from routes.order_routes import router as order_router
from config.config import MODE
from fastapi.middleware.cors import CORSMiddleware

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

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import Base, database
from routes import (
    cash_register_routes,
    employee_routes,
    invoice_routes,
    payments_routes,
    produtcts_routes,
    promotions_routes,
    sales_routes,
    stock_ajustment_routes,
    supplier_routes,
    user_routes,
)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Supermarket API", lifespan=lifespan)

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
)
origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(user_routes.router)
app.include_router(supplier_routes.router)
app.include_router(employee_routes.router)
app.include_router(produtcts_routes.router)
app.include_router(cash_register_routes.router)
app.include_router(promotions_routes.router)
app.include_router(stock_ajustment_routes.router)
app.include_router(invoice_routes.router)
app.include_router(payments_routes.router)
app.include_router(sales_routes.router)


@app.get("/")
def health_check():
    return {"status": "ok"}

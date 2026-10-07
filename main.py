from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database import Base, database
from routes.cash_register_routes import router as cash_register_router
from routes.employee_routes import router as employee_router
from routes.invoice_routes import router as invoice_router
from routes.payments_routes import router as payment_router
from routes.produtcts_routes import router as products_router
from routes.promotions_routes import router as promotions_router
from routes.sales_routes import router as sale_router
from routes.stock_ajustment_routes import router as stock_router
from routes.supplier_routes import router as supplier_router
from routes.user_routes import router as user_router

# Cria as tabelas do Banco. Ciclo de vida (Lifespan) assíncrono
"""
Como estamos criando o db direto usamos essa função,
caso o banco ja existice deixa somente a parte do FastAPi
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# Cria a Instância do FastAPI
app = FastAPI(title="supermarket", lifespan=lifespan)

# Conectando as rotas ao sistema
app.include_router(supplier_router)
app.include_router(products_router)
app.include_router(user_router)
app.include_router(employee_router)
app.include_router(promotions_router)
app.include_router(stock_router)
app.include_router(sale_router)
app.include_router(cash_register_router)
app.include_router(payment_router)
app.include_router(invoice_router)


# Rota test para swagger
@app.get("/")
async def home():
    return {"message": "SuperMarket API!"}

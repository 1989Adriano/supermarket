from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import Base, database


# Cria as tabelas do Banco. Ciclo de vida (Lifespan) assíncrono
"""
Como estamos criando o db direto usamos essa função,
caso o banco ja existice reixa somente a parte do FastAPi
"""
@asynccontextmanager
async def lifespan(app: FastAPI):   
    async with database.begin() as conn:      
        await conn.run_sync(Base.metadata.create_all)
    yield

# Cria a Instância do FastAPI 
app = FastAPI(title="supermarket", lifespan=lifespan)

# Rota test para swagger 
@app.get("/")
async def home():
    return {"message": "SuperMarket API!"}

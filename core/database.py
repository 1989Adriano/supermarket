import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Carrega as variáveis do arquivo .env
load_dotenv()

DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# Monta a URL assíncrona para o Postgres 18
URL = f"postgresql+asyncpg://postgres:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"


# Cria a o Banco SQLite3
database = create_async_engine(URL, echo=True)

# Cria a Sessão
SessionLocal = async_sessionmaker(
    bind=database, class_=AsyncSession, expire_on_commit=False
)

# Cria a Classe Main/Principal
Base = declarative_base()


# Faz a conexão com o banco e fecha apos cada ação.
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

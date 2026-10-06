from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# URL do banco
URL = 'sqlite+aiosqlite:///supermarket.db'

# Cria a o Banco SQLite3
database = create_async_engine(URL)

# Cria a Sessão 
SessionLocal = async_sessionmaker(
    bind=database, 
    class_= AsyncSession,
    expire_on_commit=False
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
            
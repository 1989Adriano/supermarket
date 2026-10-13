import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    missing_settings = [
        name
        for name, value in (
            ("DB_PASSWORD", DB_PASSWORD),
            ("DB_HOST", DB_HOST),
            ("DB_NAME", DB_NAME),
        )
        if not value
    ]
    if missing_settings:
        raise RuntimeError(
            "Database configuration is incomplete; set DATABASE_URL or "
            f"the following environment variables: {', '.join(missing_settings)}"
        )

    DB_URL = URL.create(
        "postgresql+asyncpg",
        username="postgres",
        password=DB_PASSWORD,
        host=DB_HOST,
        port=5432,
        database=DB_NAME,
    )

database = create_async_engine(DB_URL, echo=False)

SessionLocal = async_sessionmaker(
    bind=database, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

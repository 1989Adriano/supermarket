import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.database import Base, get_db
from main import app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys = OFF;"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(autouse=True)
async def override_app_db():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


async def test_create_supplier_route_success():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {
            "corporate_name": "Distribuidora Nova Ltda",
            "trade_name": "Nova Distribuidora",
            "cnpj": "98.765.432/0001-10",
            "contact_name": "João Pereira",
            "email": "contato@novadistribuidora.com",
            "phone": "(11) 99888-7766",
            "is_active": True,
            "state_registration": "654321987",
            "address": "Av. Principal, 88",
            "city": "Campinas",
            "state": "SP",
        }

        response = await client.post("/suppliers/", json=payload)

        assert response.status_code == 201
        assert response.json()["trade_name"] == "Nova Distribuidora"


async def test_get_supplier_by_id_not_found():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/suppliers/9999")

        assert response.status_code == 404
        assert "Fornecedor não encontrado" in response.json()["detail"]

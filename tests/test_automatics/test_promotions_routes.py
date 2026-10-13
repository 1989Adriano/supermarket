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


async def create_supplier(client: AsyncClient):
    payload = {
        "corporate_name": "Distribuidora do Vale Ltda",
        "trade_name": "Vale Distribuidora",
        "cnpj": "12.345.678/0001-99",
        "contact_name": "Maria da Silva",
        "email": "fornecedor@vale.com",
        "phone": "(11) 3344-5566",
        "is_active": True,
        "state_registration": "123456789",
        "address": "Rua do Fornecedor, 25",
        "city": "São Paulo",
        "state": "SP",
    }
    response = await client.post("/suppliers/", json=payload)
    assert response.status_code == 201
    return response.json()


async def create_product(client: AsyncClient, supplier_id: int):
    payload = {
        "name": "Arroz Integral",
        "brand": "Nobre",
        "code_bar": "7891234567890",
        "stock_quantity": 20,
        "min_stock": 5,
        "price": "24.90",
        "cost_price": "18.50",
        "category": "mercearia",
        "unit_type": "UN",
        "is_perishable": False,
        "expiration_date": "2026-12-31",
        "ncm_code": "1001.10",
        "supplier_id": supplier_id,
    }
    response = await client.post("/products/", json=payload)
    assert response.status_code == 201
    return response.json()


async def test_create_promotion_route_success():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        supplier = await create_supplier(client)
        product = await create_product(client, supplier["id"])

        payload = {
            "name": "Promoção de semana",
            "promotional_price": "16.90",
            "start_date": "2026-10-09T00:00:00",
            "end_date": "2026-10-16T00:00:00",
            "is_active": True,
            "product_id": product["id"],
        }

        response = await client.post("/promotions/", json=payload)

        assert response.status_code == 201
        assert response.json()["name"] == "Promoção de semana"


async def test_get_promotion_by_id_not_found():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/promotions/9999")

        assert response.status_code == 404
        assert "Promoção não encontrada" in response.json()["detail"]

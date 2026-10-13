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
        "name": "Leite Integral",
        "brand": "Bom Leite",
        "code_bar": "7894561234569",
        "stock_quantity": 15,
        "min_stock": 4,
        "price": "8.60",
        "cost_price": "6.20",
        "category": "laticinios_ovos",
        "unit_type": "UN",
        "is_perishable": True,
        "expiration_date": "2026-11-15",
        "ncm_code": "0401.10",
        "supplier_id": supplier_id,
    }
    response = await client.post("/products/", json=payload)
    assert response.status_code == 201
    return response.json()


async def test_create_invoice_route_success():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        supplier = await create_supplier(client)
        product = await create_product(client, supplier["id"])

        payload = {
            "invoice_number": "NF-2026-0001",
            "series": "1",
            "received_at": "2026-10-09T14:00:00",
            "total_amount": "98.00",
            "supplier_id": supplier["id"],
            "items": [
                {
                    "quantity": 2,
                    "unit_cost": "14.50",
                    "invoice_id": 999,
                    "product_id": product["id"],
                }
            ],
        }

        response = await client.post("/invoices/", json=payload)

        assert response.status_code == 201
        assert response.json()["invoice_number"] == "NF-2026-0001"


async def test_get_invoice_by_id_not_found():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/invoices/9999")

        assert response.status_code == 404
        assert "Nota fiscal de entrada não encontrada" in response.json()["detail"]

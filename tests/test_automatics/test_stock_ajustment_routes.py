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
        "name": "Pão Francês",
        "brand": "Padaria Bom",
        "code_bar": "7894561234568",
        "stock_quantity": 40,
        "min_stock": 10,
        "price": "12.50",
        "cost_price": "8.50",
        "category": "padaria",
        "unit_type": "UN",
        "is_perishable": False,
        "expiration_date": "2026-11-30",
        "ncm_code": "1905.90",
        "supplier_id": supplier_id,
    }
    response = await client.post("/products/", json=payload)
    assert response.status_code == 201
    return response.json()


async def create_employee(client: AsyncClient):
    payload = {
        "first_name": "Patricia",
        "middle_name": "Moura",
        "last_name": "Costa",
        "address_line_1": "Rua do Estoque, 22",
        "city": "São Paulo",
        "neighborhood": "Jardim",
        "state": "SP",
        "email": "patricia.estoque@supermercado.com",
        "cpf": "222.333.444-55",
        "birthday": "1993-06-30",
        "phone1": "(11) 97777-3333",
        "is_active": True,
        "complement_id": None,
        "pis_pasep": "22233344455",
        "ctps_number": "9988776655",
        "admission_date": "2022-01-10",
        "salary": "3700.00",
        "role_title": "repositor_mercadorias",
    }
    response = await client.post("/employee/", json=payload)
    assert response.status_code == 201
    return response.json()


async def test_create_stock_adjustment_route_success():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        supplier = await create_supplier(client)
        product = await create_product(client, supplier["id"])
        employee = await create_employee(client)

        payload = {
            "quantity": 5,
            "adjusted_at": "2026-10-09T10:00:00",
            "reason": "consumo_interno",
            "notes": "Ajuste de inventário",
            "product_id": product["id"],
            "employee_id": employee["id"],
        }

        response = await client.post("/stock_ajustment/", json=payload)

        assert response.status_code == 201
        assert response.json()["reason"] == "consumo_interno"


async def test_get_stock_adjustment_by_id_not_found():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/stock_ajustment/9999")

        assert response.status_code == 404
        assert "Registro de perdas não encontrado" in response.json()["detail"]

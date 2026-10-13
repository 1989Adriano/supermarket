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


async def create_employee(client: AsyncClient):
    payload = {
        "first_name": "Ana",
        "middle_name": "Paula",
        "last_name": "Lima",
        "address_line_1": "Rua do Caixa, 10",
        "city": "São Paulo",
        "neighborhood": "Centro",
        "state": "SP",
        "email": "ana.caixa@supermercado.com",
        "cpf": "333.444.555-66",
        "birthday": "1994-04-10",
        "phone1": "(11) 98877-3311",
        "is_active": True,
        "complement_id": None,
        "pis_pasep": "33344455566",
        "ctps_number": "2030405060",
        "admission_date": "2023-01-20",
        "salary": "4200.00",
        "role_title": "operador_caixa",
    }
    response = await client.post("/employee/", json=payload)
    assert response.status_code == 201
    return response.json()


async def create_sale(client: AsyncClient, cashier_id: int):
    payload = {
        "receipt_number": "CUPOM-PAG-001",
        "subtotal": "120.00",
        "discount": "10.00",
        "total_amount": "110.00",
        "payment_method": "dinheiro",
        "client_cpf": "111.222.333-44",
        "cashier_id": cashier_id,
    }
    response = await client.post("/sales/", json=payload)
    assert response.status_code == 201
    return response.json()


async def test_create_payment_route_success():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        employee = await create_employee(client)
        sale = await create_sale(client, employee["id"])

        payload = {
            "amount": "150.50",
            "transaction_date": "2026-10-09T12:00:00",
            "acquirer": "Stone",
            "authorization_code": "NSU-123456",
            "status": "aprovada",
            "sale_id": sale["id"],
        }

        response = await client.post("/payments/", json=payload)

        assert response.status_code == 201
        assert response.json()["amount"] == "150.50"


async def test_get_payment_by_id_not_found():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/payments/9999")

        assert response.status_code == 404
        assert "Pagamento não encontrado" in response.json()["detail"]

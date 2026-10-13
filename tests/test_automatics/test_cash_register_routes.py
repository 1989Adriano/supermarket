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


# Dados Ficticios
async def create_employee(client: AsyncClient):
    payload = {
        "first_name": "Carlos",
        "middle_name": "Eduardo",
        "last_name": "Silva",
        "address_line_1": "Rua das Flores, 100",
        "city": "São Paulo",
        "neighborhood": "Centro",
        "state": "SP",
        "email": "carlos.funcionario@supermercado.com",
        "cpf": "123.456.789-01",
        "birthday": "1990-05-15",
        "phone1": "(11) 98888-7777",
        "is_active": True,
        "complement_id": None,
        "pis_pasep": "12345678901",
        "ctps_number": "9876543210",
        "admission_date": "2021-02-20",
        "salary": "3500.00",
        "role_title": "empacotador",
    }
    response = await client.post("/employee/", json=payload)
    assert response.status_code == 201
    return response.json()


async def test_create_cash_register_route_success():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        employee = await create_employee(client)

        payload = {
            "terminal_number": "CAIXA01",
            "opened_at": "2026-10-09T08:00:00",
            "closed_at": None,
            "opening_balance": "150.00",
            "closing_balance": None,
            "status": "Aberto",
            "cashier_id": employee["id"],
        }

        response = await client.post("/cash_register/", json=payload)

        assert response.status_code == 201
        assert response.json()["terminal_number"] == "CAIXA01"


async def test_get_cash_register_by_id_not_found():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/cash_register/9999")

        assert response.status_code == 404
        assert "Entrada de caixa não encontrada" in response.json()["detail"]

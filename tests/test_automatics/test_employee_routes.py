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


async def test_create_employee_route_success():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {
            "first_name": "Fernanda",
            "middle_name": "Lívia",
            "last_name": "Souza",
            "address_line_1": "Rua das Palmeiras, 44",
            "city": "São Paulo",
            "neighborhood": "Vila Nova",
            "state": "SP",
            "email": "fernanda@supermercado.com",
            "cpf": "987.654.321-00",
            "birthday": "1992-11-02",
            "phone1": "(11) 97654-1212",
            "is_active": True,
            "complement_id": None,
            "pis_pasep": "98765432109",
            "ctps_number": "1122334455",
            "admission_date": "2020-07-01",
            "salary": "4100.00",
            "role_title": "empacotador",
        }

        response = await client.post("/employee/", json=payload)

        assert response.status_code == 201
        assert response.json()["first_name"] == "Fernanda"


async def test_get_employee_by_id_not_found():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/employee/9999")

        assert response.status_code == 404
        assert "Funcionário não encontrado" in response.json()["detail"]

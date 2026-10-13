import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.database import Base, get_db
from main import app
from models.user_model import Users

# Setup do Banco de Dados Temporário em Memória
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(autouse=True)
async def setup_database():
    """Cria as tabelas na memória antes de testar a rota e apaga depois."""
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys = OFF;"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    """Substitui o banco de dados real do Postgres pelo SQLite em memória."""
    async with TestingSessionLocal() as session:
        yield session



@pytest.fixture(autouse=True)
async def override_app_db():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


# Payload padrão válido
PAYLOAD_VALIDO = {
    "first_name": "Adriano",
    "last_name": "Analista",
    "cpf": "123.456.789-00",
    "email": "adriano@supermercado.com",
    "address_line_1": "Rua Central, 100",
    "neighborhood": "Centro",
    "state": "SP",
    "birthday": "1995-10-09",
    "phone1": "(11) 99999-9999",
    "complement_id": None,
}

async def test_create_user_route_e2e_success():
    """Simula uma requisição HTTP real enviando os dados exatos exigidos pela BaseMotherSchema."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/users/", json=PAYLOAD_VALIDO)

        assert response.status_code == 201
        json_data = response.json()
        assert json_data["id"] is not None
        assert json_data["first_name"] == "Adriano"


async def test_create_user_route_pydantic_validation_error():
    """Garante que o Schema Pydantic barra na entrada se mandarmos campos com tipos errados."""
    payload_dados_errados = PAYLOAD_VALIDO.copy()
    payload_dados_errados["complement_id"] = "TextoInvalido"

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/users/", json=payload_dados_errados)
        assert response.status_code == 422


async def test_get_user_by_id_success():
    """Garante que a rota retorna os dados corretos de um usuário existente (HTTP 200)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        
        # Primeiro cria o usuário para ele existir no banco em memória
        create_resp = await client.post("/users/", json=PAYLOAD_VALIDO)
        user_id = create_resp.json()["id"]

        # Executa a busca pelo ID gerado diretamente na rota GET
        response = await client.get(f"/users/{user_id}")

        assert response.status_code == 200
        json_data = response.json()
        assert json_data["id"] == user_id
        assert json_data["first_name"] == "Adriano"


async def test_get_user_by_id_not_found():
    """Garante que a rota retorna erro 404 controlado se o usuário não existir."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Tenta buscar um ID absurdo que nunca foi cadastrado (ex: 9999)
        response = await client.get("/users/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Usuário não encontrado!"

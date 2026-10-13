import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# IMPORTS BASE DE CONFIGURAÇÃO
from core.database import Base, get_db
from main import app

# IMPORTS DE TODAS AS MODELS ENVOLVIDAS
from models.sale_model import Sales
from models.user_model import Users

try:
    from models.employee_model import Employee, EmployeeComplements
    _force_registry = (Sales, Users, Employee, EmployeeComplements)
except ImportError:
    _force_registry = (Sales, Users)

# Setup do Banco de Dados Temporário em Memória exclusivo para o teste de vendas
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture(autouse=True)
async def setup_database():
    """Garante que TODAS as tabelas do projeto existam no banco em memória antes de cada teste."""
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys = OFF;"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def override_get_db():
    """Injeta a sessão em memória no lugar do PostgreSQL físico."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(autouse=True)
async def override_app_db():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


# Payload padrão de usuário exigido pela sua BaseMotherSchema
PAYLOAD_OPERADOR = {
    "first_name": "Juliana",
    "last_name": "Caixa",
    "cpf": "987.654.321-11",
    "email": "juliana@supermercado.com",
    "address_line_1": "Rua das Flores, 50",
    "neighborhood": "Bairro Alto",
    "state": "SP",
    "birthday": "1998-05-15",
    "phone1": "(11) 98888-8888",
    "complement_id": None
}

async def test_create_sale_route_e2e_success():
    """Garante que a rota cria um cupom fiscal com sucesso quando o operador existe."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        
        # Cria o operador do caixa primeiro na tabela correspondente (Gera o ID válido)
        user_resp = await client.post("/users/", json=PAYLOAD_OPERADOR)
        assert user_resp.status_code == 201, f"Erro ao criar operador base: {user_resp.json()}"
        cashier_id = user_resp.json()["id"]

        # Prepara o cupom de vendas mapeado no seu SalesRequest real
        sale_payload = {
            "receipt_number": "CUPOM-E2E-001",
            "subtotal": 120.50,
            "discount": 5.50,
            "total_amount": 115.00,
            "payment_method": "dinheiro",
            "client_cpf": "111.222.333-44",
            "cashier_id": cashier_id
        }

        # Dispara rota de vendas POST /sales/
        response = await client.post("/sales/", json=sale_payload)

        assert response.status_code == 201, f"Erro na rota de vendas: {response.json()}"
        json_data = response.json()
        assert json_data["id"] is not None
        assert json_data["receipt_number"] == "CUPOM-E2E-001"


async def test_create_sale_route_pydantic_cpf_too_short():
    """Garante que o Schema de vendas barra CPFs menores que 14 caracteres."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user_resp = await client.post("/users/", json=PAYLOAD_OPERADOR)
        cashier_id = user_resp.json()["id"]

        sale_payload_errado = {
            "receipt_number": "CUPOM-E2E-002",
            "subtotal": 50.00,
            "discount": 0.00,
            "total_amount": 50.00,
            "payment_method": "dinheiro",
            "client_cpf": "11122233344",
            "cashier_id": cashier_id
        }

        response = await client.post("/sales/", json=sale_payload_errado)
        assert response.status_code == 422


async def test_get_sale_by_id_not_found():
    """Garante que buscar um cupom fiscal invisível retorna erro controlado 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/sales/9999")
        
        assert response.status_code == 404
        assert "venda não encontrada" in response.json()["detail"].lower()

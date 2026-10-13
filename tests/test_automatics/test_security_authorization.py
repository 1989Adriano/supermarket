from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.requests import Request

import core.security as security
from core.database import Base
from core.security import hash_password
from models.user_model import UserComplements, Users
from repositories.user_repository import UserRespository

_ = UserComplements
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _create_user(db: AsyncSession, *, role: str, is_active: bool = True) -> Users:
    user = Users(
        first_name="Test",
        last_name="Account",
        address_line_1="Test Street",
        neighborhood="Central",
        state="SP",
        email=f"{role}-{is_active}@example.com",
        cpf=f"{'1' if role == 'admin' else '2'}2345678901",
        birthday=date(1990, 1, 1),
        phone1="11999999999",
        password_hash=hash_password("test-password"),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def _request_with_token(token: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/protected",
            "headers": [(b"authorization", f"Bearer {token}".encode())],
        }
    )


async def test_authenticated_non_admin_is_forbidden():
    async with TestingSessionLocal() as db:
        user = await _create_user(db, role="user")
        request = _request_with_token(
            security.create_access_token(str(user.id), "user")
        )

        with pytest.raises(HTTPException) as error:
            await security.require_admin(request, db)

    assert error.value.status_code == 403


async def test_admin_token_is_authorized():
    async with TestingSessionLocal() as db:
        user = await _create_user(db, role="admin")
        request = _request_with_token(
            security.create_access_token(str(user.id), "admin")
        )

        payload = await security.require_admin(request, db)

    assert payload["sub"] == str(user.id)
    assert payload["role"] == "admin"


async def test_deactivated_admin_token_is_rejected():
    async with TestingSessionLocal() as db:
        user = await _create_user(db, role="admin", is_active=False)
        request = _request_with_token(
            security.create_access_token(str(user.id), "admin")
        )

        with pytest.raises(HTTPException) as error:
            await security.require_admin(request, db)

    assert error.value.status_code == 401


async def test_old_admin_token_is_rejected_after_role_demotion():
    async with TestingSessionLocal() as db:
        user = await _create_user(db, role="user")
        stale_admin_token = security.create_access_token(str(user.id), "admin")
        request = _request_with_token(stale_admin_token)

        with pytest.raises(HTTPException) as error:
            await security.require_admin(request, db)

    assert error.value.status_code == 403


async def test_inactive_user_cannot_authenticate():
    async with TestingSessionLocal() as db:
        user = await _create_user(db, role="admin", is_active=False)

        authenticated = await UserRespository(db).authenticate_user(
            user.email, "test-password"
        )

    assert authenticated is None


async def test_missing_token_is_rejected_even_if_auth_required_is_false(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "false")
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/protected",
            "headers": [],
        }
    )

    async with TestingSessionLocal() as db:
        with pytest.raises(HTTPException) as error:
            await security.require_admin(request, db)

    assert error.value.status_code == 401

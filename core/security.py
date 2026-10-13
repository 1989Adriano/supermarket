import hashlib
import os
import secrets
import time
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user_model import Users

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
configured_jwt_secret = os.getenv("JWT_SECRET")
if APP_ENV in {"prod", "production"}:
    if not configured_jwt_secret:
        raise RuntimeError("JWT_SECRET must be configured in production.")
    if len(configured_jwt_secret) < 32:
        raise RuntimeError(
            "JWT_SECRET must contain at least 32 characters in production."
        )

JWT_SECRET = configured_jwt_secret or secrets.token_urlsafe(32)
JWT_ALGORITHM = "HS256"
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "3600"))


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000,
    )
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash or not password_hash.startswith("pbkdf2_sha256$"):
        return False

    _, salt, expected = password_hash.split("$", 2)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000,
    )
    return secrets.compare_digest(digest.hex(), expected)


def create_access_token(subject: str, role: str = "user") -> str:
    payload = {
        "sub": subject,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_TTL_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def require_auth(request: Request) -> dict[str, Any]:
    authorization = request.headers.get("authorization", "")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação obrigatória.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    if not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    request.state.user = payload
    return payload


async def require_admin(
    request: Request, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    payload = await require_auth(request)
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    result = await db.execute(select(Users).where(Users.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta inativa ou inexistente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if str(user.role).strip().lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente.",
        )

    current_user = {**payload, "role": user.role}
    request.state.user = current_user
    return current_user

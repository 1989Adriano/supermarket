from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import require_admin
from core.security import create_access_token
from repositories.user_repository import UserRespository
from schemas.user_schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRequest,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_user(payload: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRespository(db)
    user = await repo.authenticate_user(payload.email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(str(user.id), getattr(user, "role", "user"))
    return TokenResponse(access_token=token)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserRequest, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    repo = UserRespository(db)
    new_user = await repo.create_user(payload.model_dump(exclude_none=True))
    return new_user


@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    repo = UserRespository(db)
    return await repo.get_all_users()


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_id(user_id: int, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    repo = UserRespository(db)
    search_id = await repo.get_user_by_id(user_id)

    if not search_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado!"
        )
    return search_id


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)
):
    repo = UserRespository(db)
    user_updated = await repo.update_user(user_id, payload.model_dump(exclude_unset=True))

    if not user_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado!"
        )
    return user_updated


@router.delete(
    "/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    repo = UserRespository(db)
    user_deleted = await repo.delete_user(user_id)

    if not user_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado!"
        )
    return user_deleted

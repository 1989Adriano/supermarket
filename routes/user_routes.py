from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from repositories.user_repository import UserRespository
from schemas.user_schemas import UserRequest, UserResponse, UserUpdate

# Instâcia as rotas
router = APIRouter(prefix="/users", tags=["Users"])


# Create
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserRequest, db: AsyncSession = Depends(get_db)):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = UserRespository(db)
    new_user = await repo.create_user(payload.model_dump())
    return new_user


# Read All
@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(db: AsyncSession = Depends(get_db)):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = UserRespository(db)
    new_search = await repo.get_all_users()
    return new_search


# Read by ID
@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_id(user_id: int, db: AsyncSession = Depends(get_db)):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = UserRespository(db)
    search_id = await repo.get_user_by_id(user_id)

    if not search_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado!"
        )
    return search_id


# Update
@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)
):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = UserRespository(db)
    user_updated = await repo.update_user(
        user_id, payload.model_dump(exclude_unset=True)
    )

    if not user_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado!"
        )
    return user_updated


# Delete
@router.delete(
    "/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = UserRespository(db)
    user_deleted = await repo.delete_user(user_id)

    if not user_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado!"
        )
    return user_deleted

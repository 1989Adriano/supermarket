from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from repositories.cash_register_repository import CashRegisterSessionRepository
from schemas.cash_register_schemas import (
    CashRegisterRequest,
    CashRegisterResponse,
    CashRegisterUpdate,
)

# Instâcia as rotas
router = APIRouter(prefix="/cash_register", tags=["Cash_register"])


# Create
@router.post(
    "/", response_model=CashRegisterResponse, status_code=status.HTTP_201_CREATED
)
async def create_cash_register(
    payload: CashRegisterRequest, db: AsyncSession = Depends(get_db)
):
    repo = CashRegisterSessionRepository(db)
    new_cash_in = await repo.create_cash_register(payload.model_dump())
    return new_cash_in


# Read All
@router.get(
    "/", response_model=list[CashRegisterResponse], status_code=status.HTTP_200_OK
)
async def get_all_cash_register(db: AsyncSession = Depends(get_db)):
    repo = CashRegisterSessionRepository(db)
    new_search = await repo.get_all_cash_register()
    return new_search


# Read by ID
@router.get(
    "/{cash_id}",
    response_model=CashRegisterResponse,
    status_code=status.HTTP_200_OK,
)
async def get_cash_register_id(cash_id: int, db: AsyncSession = Depends(get_db)):
    repo = CashRegisterSessionRepository(db)
    new_search = await repo.get_cash_register_by_id(cash_id)

    if not new_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada de caixa não encontrada!",
        )
    return new_search


# Update
@router.put(
    "/{cash_id}", response_model=CashRegisterResponse, status_code=status.HTTP_200_OK
)
async def update_cash_register(
    cash_id: int, payload: CashRegisterUpdate, db: AsyncSession = Depends(get_db)
):
    repo = CashRegisterSessionRepository(db)
    cash_registered_updated = await repo.update_cash_register(
        cash_id, payload.model_dump(exclude_unset=True)
    )

    if not cash_registered_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada de caixa não encontrada!",
        )
    return cash_registered_updated


# Delete
@router.delete(
    "/{cash_id}", response_model=CashRegisterResponse, status_code=status.HTTP_200_OK
)
async def delete_cash_register(cash_id: int, db: AsyncSession = Depends(get_db)):
    repo = CashRegisterSessionRepository(db)
    cash_registered_deleted = await repo.delete_cash_register(cash_id)

    if not cash_registered_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada de caixa não encontrada!",
        )
    return cash_registered_deleted

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from repositories.stock_ajustment_repository import StockAdjustmentRepository
from schemas.stock_adjustment_schema import (
    StockAdjustmentRequest,
    StockAdjustmentResponse,
    StockAdjustmentUpdate,
)

# Instância as rotas
router = APIRouter(prefix="/stock_ajustment", tags=["Stock_ajustment"])


# Create
@router.post(
    "/", response_model=StockAdjustmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_stock(
    payload: StockAdjustmentRequest, db: AsyncSession = Depends(get_db)
):

    repo = StockAdjustmentRepository(db)
    new_stock = await repo.create_stock_adjustment(payload.model_dump())
    return new_stock


# Read All
@router.get("/", response_model=list[StockAdjustmentResponse], status_code=status.HTTP_200_OK)
async def get_all_stock(db: AsyncSession = Depends(get_db)):
    repo = StockAdjustmentRepository(db)
    new_search = await repo.get_all_stock_adjustment()
    return new_search


# Read by ID
@router.get(
    "/{stock_id}",
    response_model=StockAdjustmentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_stock_id(stock_id: int, db: AsyncSession = Depends(get_db)):
    repo = StockAdjustmentRepository(db)
    new_search = await repo.get_stock_adjustment_by_id(stock_id)

    if not new_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de perdas não encontrado!",
        )
    return new_search


# Update
@router.put(
    "/{stock_id}",
    response_model=StockAdjustmentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_stock(
    stock_id: int, payload: StockAdjustmentUpdate, db: AsyncSession = Depends(get_db)
):

    repo = StockAdjustmentRepository(db)
    stock_updated = await repo.update_stock_adjustment(
        stock_id, payload.model_dump(exclude_unset=True)
    )

    if not stock_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de perdas não encontrado!",
        )
    return stock_updated


# Delete
@router.delete(
    "/{stock_id}",
    response_model=StockAdjustmentResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_stock(stock_id: int, db: AsyncSession = Depends(get_db)):
    repo = StockAdjustmentRepository(db)
    stock_deleted = await repo.delete_stock_adjustment(stock_id)

    if not stock_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de perdas não encontrado!",
        )
    return stock_deleted

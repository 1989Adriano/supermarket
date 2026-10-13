from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import require_admin
from repositories.promotions_repository import PromotionsRepository
from schemas.promotions_schema import (
    PromotionsRequest,
    PromotionsResponse,
    PromotionsUpdate,
)

# Instância as rotas
router = APIRouter(prefix="/promotions", tags=["Promotions"])


# Create
@router.post(
    "/", response_model=PromotionsResponse, status_code=status.HTTP_201_CREATED
)
async def create_promotions(
    payload: PromotionsRequest, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)
):

    repo = PromotionsRepository(db)
    new_promotion = await repo.create_promotions(payload.model_dump())
    return new_promotion


# Read All
@router.get(
    "/", response_model=list[PromotionsResponse], status_code=status.HTTP_200_OK
)
async def get_all_promotion(db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):

    repo = PromotionsRepository(db)
    new_search = await repo.get_all_promotions()
    return new_search


# Read by ID
@router.get(
    "/{promotion_id}", response_model=PromotionsResponse, status_code=status.HTTP_200_OK
)
async def get_promotion_id(promotion_id: int, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):

    repo = PromotionsRepository(db)
    new_search = await repo.get_promotions_by_id(promotion_id)

    if not new_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Promoção não encontrada!"
        )
    return new_search


# Update
@router.put(
    "/{promotion_id}", response_model=PromotionsResponse, status_code=status.HTTP_200_OK
)
async def update_promotion(
    promotion_id: int, payload: PromotionsUpdate, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)
):

    repo = PromotionsRepository(db)
    promotion_updated = await repo.update_promotions(
        promotion_id, payload.model_dump(exclude_unset=True)
    )

    if not promotion_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Promoção não encontrada!"
        )
    return promotion_updated


# Delete
@router.delete(
    "/{promotion_id}", response_model=PromotionsResponse, status_code=status.HTTP_200_OK
)
async def delete_promotion(promotion_id: int, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):

    repo = PromotionsRepository(db)
    promotion_deleted = await repo.delete_promotion(promotion_id)

    if not promotion_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Promoção não encontrada!"
        )
    return promotion_deleted

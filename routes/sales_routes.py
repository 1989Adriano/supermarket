from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import require_admin
from repositories.sales_repository import SalesRepository
from schemas.sale_schemas import SalesRequest, SalesResponse, SalesUpdate

# Instância as rotas
router = APIRouter(prefix="/sales", tags=["Sales"])


# Create
@router.post("/", response_model=SalesResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(payload: SalesRequest, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    repo = SalesRepository(db)  

    new_sale = await repo.create_sale(sale_data=payload.model_dump(), items_data=[])
    return new_sale


# Read All
@router.get("/", response_model=list[SalesResponse], status_code=status.HTTP_200_OK)
async def get_all_sales(db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    repo = SalesRepository(db)

    # Passa os dados do cupom e envia uma lista vazia [] para os itens
    new_search = await repo.get_all_sales()
    return new_search


# Read by ID
@router.get("/{sale_id}", response_model=SalesResponse, status_code=status.HTTP_200_OK)
async def get_sales_id(sale_id: int, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    repo = SalesRepository(db)
    new_search = await repo.get_sale_by_id(sale_id)

    if not new_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Venda não encontrada!"
        )
    return new_search


# Update
@router.put("/{sale_id}", response_model=SalesResponse, status_code=status.HTTP_200_OK)
async def update_sale(
    sale_id: int, payload: SalesUpdate, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)
):
    repo = SalesRepository(db)
    sale_updated = await repo.update_sale(
        sale_id, payload.model_dump(exclude_unset=True)
    )

    if not sale_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Venda não encontrada!"
        )
    return sale_updated


# Delete
@router.delete(
    "/{sale_id}", response_model=SalesResponse, status_code=status.HTTP_200_OK
)
async def delete_sale(sale_id: int, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    repo = SalesRepository(db)
    sale_deleted = await repo.delete_sale(sale_id)

    if not sale_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Venda não encontrada!"
        )
    return sale_deleted

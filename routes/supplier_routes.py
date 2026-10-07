from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from repositories.supplier_repository import SupplierRepository
from schemas.supplier_schemas import SupplierRequest, SupplierResponse, SupplierUpdate

# Instância a rota
router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


# Create
@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_new_supplier(
    payload: SupplierRequest, db: AsyncSession = Depends(get_db)
):
    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = SupplierRepository(db)
    new_supplier = await repo.create_supplier(payload.model_dump())
    return new_supplier


# Read All
@router.get("/", response_model=list[SupplierResponse], status_code=status.HTTP_200_OK)
async def get_supplies(db: AsyncSession = Depends(get_db)):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = SupplierRepository(db)
    new_search = await repo.get_all_supplier()
    return new_search


# Read by ID
@router.get(
    "/{supplier_id}", response_model=SupplierResponse, status_code=status.HTTP_200_OK
)
async def get_supplies_id(supplier_id: int, db: AsyncSession = Depends(get_db)):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = SupplierRepository(db)
    supplier = await repo.get_supplier_by_id(supplier_id)

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado no sistema!",
        )

    return supplier


# Update
@router.put(
    "/{supplier_id}", response_model=SupplierResponse, status_code=status.HTTP_200_OK
)
async def update_supply(
    supplier_id: int, payload: SupplierUpdate, db: AsyncSession = Depends(get_db)
):
    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = SupplierRepository(db)
    supplier_updated = await repo.update_supplier(
        supplier_id, payload.model_dump(exclude_unset=True)
    )

    if not supplier_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado no sistema!",
        )

    return supplier_updated


# Delete
@router.delete(
    "/{supplier_id}", response_model=SupplierResponse, status_code=status.HTTP_200_OK
)
async def delete_supply(supplier_id: int, db: AsyncSession = Depends(get_db)):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = SupplierRepository(db)
    supplier_deleted = await repo.delete_supplier(supplier_id)

    if not supplier_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado no sistema!",
        )

    return supplier_deleted

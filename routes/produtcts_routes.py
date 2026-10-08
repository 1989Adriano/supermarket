from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from repositories.products_repository import ProductsRepository
from schemas.product_schemas import ProductRequest, ProductResponse, ProductUpate

# Instância das rotas
router = APIRouter(prefix="/products", tags=["Products"])


# Create
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    payload: ProductRequest, db: AsyncSession = Depends(get_db)
):

    # Instância a classe do repositoty(db: liga/desliga a sessão)
    repo = ProductsRepository(db)
    new_products = await repo.create_product(payload.model_dump())
    return new_products


# Read All
@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_db)):

    # Instância a classe do repositoty(db: liga/desliga a sessão)
    repo = ProductsRepository(db)
    new_search = await repo.get_all_products()
    return new_search


# Read by ID
@router.get(
    "/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
async def get_products_id(product_id: int, db: AsyncSession = Depends(get_db)):

    # Instância a classe do repositoty(db: liga/desliga a sessão)
    repo = ProductsRepository(db)
    new_search = await repo.get_products_by_id(product_id)

    if not new_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado!"
        )
    return new_search


# Update
@router.put(
    "/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
async def update_products(
    product_id: int, payload: ProductUpate, db: AsyncSession = Depends(get_db)
):

    # Instância a classe do repositoty(db: liga/desliga a sessão)
    repo = ProductsRepository(db)
    product_updated = await repo.update_products(
        product_id, payload.model_dump(exclude_unset=True)
    )

    if not product_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado!"
        )
    return product_updated


# Delete
@router.delete(
    "/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
async def delete_products(product_id: int, db: AsyncSession = Depends(get_db)):
    repo = ProductsRepository(db)
    product_deleted = await repo.delete_products(product_id)

    # Instância a classe do repositoty(db: liga/desliga a sessão)
    if not product_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado!"
        )
    return product_deleted

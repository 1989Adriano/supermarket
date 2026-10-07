from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from repositories.invoice_repository import InvoiceRepository
from schemas.invoice_schemas import InvoicesRequest, InvoicesResponse, InvoicesUpdate

# Instância as rotas
router = APIRouter(prefix="/invoices", tags=["Invoices"])


# Create
@router.post("/", response_model=InvoicesResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(payload: InvoicesRequest, db: AsyncSession = Depends(get_db)):
    repo = InvoiceRepository(db)

    # Isola os dados fiscais da nota(remove o cabeçalho)
    invoice_data = payload.model_dump(exclude={"items"})

    # Isola a lista de itens/produtos que estão dando entrada no estoque do mercado
    items_data = [item for item in payload.items] if payload.items else []

    new_invoice = await repo.create_invoice(invoice_data, items_data)
    return new_invoice


# Read All
@router.get("/", response_model=list[InvoicesResponse], status_code=status.HTTP_200_OK)
async def get_all_invoices(db: AsyncSession = Depends(get_db)):
    repo = InvoiceRepository(db)
    new_search = await repo.get_all_invoices()
    return new_search


# Read by ID
@router.get(
    "/{invoice_id}", response_model=InvoicesResponse, status_code=status.HTTP_200_OK
)
async def get_invoice_by_id(invoice_id: int, db: AsyncSession = Depends(get_db)):
    repo = InvoiceRepository(db)
    new_search = await repo.get_invoice_by_id(invoice_id)

    if not new_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal de entrada não encontrada!",
        )
    return new_search


# Update
@router.put(
    "/{invoice_id}", response_model=InvoicesResponse, status_code=status.HTTP_200_OK
)
async def update_invoice(
    invoice_id: int, payload: InvoicesUpdate, db: AsyncSession = Depends(get_db)
):
    repo = InvoiceRepository(db)
    invoice_updated = await repo.update_invoice(
        invoice_id, payload.model_dump(exclude_unset=True)
    )

    if not invoice_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal de entrada não encontrada!",
        )
    return invoice_updated


# Delete
@router.delete(
    "/{invoice_id}", response_model=InvoicesResponse, status_code=status.HTTP_200_OK
)
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    repo = InvoiceRepository(db)
    invoice_deleted = await repo.delete_invoice(invoice_id)

    if not invoice_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal de entrada não encontrada!",
        )
    return invoice_deleted

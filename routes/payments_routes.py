from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.payments_repository import PaymentsRepository
from schemas.payments_schemas import PaymentRequest, PaymentResponse, PaymentUpdate
from core.database import get_db


# Instância das rotas
router = APIRouter(prefix="/payments", tags=["Payments"])


# Create
@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payload: PaymentRequest, db: AsyncSession = Depends(get_db)):
    repo = PaymentsRepository(db)
    new_payment = await repo.create_payment(payload.model_dump())
    return new_payment


# Read All
@router.get("/", response_model=list[PaymentResponse], status_code=status.HTTP_200_OK)
async def get_all_payment(db: AsyncSession = Depends(get_db)):
    repo = PaymentsRepository(db)
    new_search = await repo.get_all_payments()
    return new_search


# Read by All
@router.get(
    "/{payments_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK
)
async def get_payment_id(payments_id: int, db: AsyncSession = Depends(get_db)):
    repo = PaymentsRepository(db)
    new_search = await repo.get_payments_by_id(payments_id)

    if not new_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pagamento não encontrado!"
        )
    return new_search


# Update
"""
Não foi criado update para segurança do Sistema, pois seria errado e 
também atrapalharia todo o financeiro uma vez que foi lançada no sistema(impostos, receitas,)
tudo seria facilmente infligido.
"""


# Delete
@router.delete(
    "/{payments_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK
)
async def delete_payment(payments_id: int, db: AsyncSession = Depends(get_db)):
    repo = PaymentsRepository(db)
    payment_deleted = await repo.delete_payments(payments_id)

    if not payment_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pagamento não encontrado!"
        )
    return payment_deleted

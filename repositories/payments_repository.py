from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.payments_model import PaymentTransactions


class PaymentsRepository:
    """
    Repositório de Conciliação Financeira.
    Gerencia o registro de transações eletrônicas, capturando dados de cartões,
    Pix e códigos de autorização NSU vinculados aos recebimentos das vendas.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_payment(self, data: dict) -> PaymentTransactions:
        """Recebe e Le o dicionário vindo da rota."""
        try: 
            new_payment = PaymentTransactions(**data)

            self.session.add(new_payment)
            await self.session.commit()
            await self.session.refresh(new_payment)
            return new_payment

        except IntegrityError as e:
            await self.session.rollback()
            error_msg = str(e.orig).lower()

            # Status de Erro para se houver colisão de vendas inexistentes
            if "foreign key" in error_msg or "sale" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não foi possível registrar o pagamento! O ID da venda (sale_id) informado não existe no sistema."
                )

            # Tratamento genérico de segurança generico Erro 500
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de integridade ao salvar a transação financeira. Verifique os relacionamentos."
            )

    # Read All
    async def get_all_payments(self) -> list[PaymentTransactions]:
        result = await self.session.execute(select(PaymentTransactions))

        return result.scalars().all()

    # Read by ID
    async def get_payments_by_id(self, payments_id: int) -> PaymentTransactions | None:
        result = await self.session.execute(
            select(PaymentTransactions).where(PaymentTransactions.id == payments_id)
        )

        return result.scalar_one_or_none()

    # Delete
    async def delete_payments(self, payments_id: int) -> PaymentTransactions | None:
        result = await self.session.execute(
            select(PaymentTransactions).where(PaymentTransactions.id == payments_id)
        )

        # Se existe cai no if, se não retorna None
        payments_exist = result.scalar_one_or_none()

        if payments_exist:
            await self.session.delete(payments_exist)
            await self.session.commit()

            return payments_exist
        return None

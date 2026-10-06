from sqlalchemy import select
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
        new_payment = PaymentTransactions(**data)

        self.session.add(new_payment)
        await self.session.commit()
        await self.session.refresh(new_payment)

        return new_payment

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
    async def delte_payments(self, payments_id: int) -> PaymentTransactions | None:
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

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.cash_register_model import CashRegisterSession


class CashRegisterSessionRepository:
    """
    Repositório de Operações de Caixa.
    Gerencia a abertura, fechamento, monitoramento de status ("Aberto"/"Fechado")
    e a conciliação financeira do saldo da gaveta de dinheiro de cada terminal do PDV.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_cash_register(self, data: dict) -> CashRegisterSession:
        """Recebe e Le o dicionário vindo da rota."""
        try:
            new_register = CashRegisterSession(**data)

            self.session.add(new_register)
            await self.session.commit()
            await self.session.refresh(new_register)
            return new_register

        except IntegrityError as e:
            await self.session.rollback()
            error_msg = str(e.orig).lower()

            # Verifica Se o funcionário informado não existe
            if (
                "foreign key" in error_msg
                or "employee" in error_msg
                or "user" in error_msg
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não foi possível abrir o caixa! O ID do funcionário/operador informado não existe no sistema.",
                )

            # Tratamento genérico de segurança generico Erro 500
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de integridade de dados ao registrar a sessão de caixa. Verifique os parâmetros informados.",
            )

    # Read All
    async def get_all_cash_register(self) -> list[CashRegisterSession]:
        result = await self.session.execute(select(CashRegisterSession))

        return result.scalars().all()

    # Read by ID
    async def get_cash_register_by_id(self, cash_id: int) -> CashRegisterSession | None:
        result = await self.session.execute(
            select(CashRegisterSession).where(CashRegisterSession.id == cash_id)
        )

        # Se existe retorna ID, se não retorna None.
        return result.scalar_one_or_none()

    # Update
    async def update_cash_register(
        self, cash_id: int, data: dict
    ) -> CashRegisterSession | None:
        result = await self.session.execute(
            select(CashRegisterSession).where(CashRegisterSession.id == cash_id)
        )

        # Se existe cai no if, se não retorna None.
        cash_register_exist = result.scalar_one_or_none()

        if cash_register_exist:
            for field, value in data.items():
                if value is not None:
                    setattr(cash_register_exist, field, value)

            await self.session.commit()
            await self.session.refresh(cash_register_exist)

            return cash_register_exist
        return None

    # Delete
    async def delete_cash_register(self, cash_id: int) -> CashRegisterSession | None:
        result = await self.session.execute(
            select(CashRegisterSession).where(CashRegisterSession.id == cash_id)
        )

        # Se existe cai no if, se não retorna None.
        cash_register_exist = result.scalar_one_or_none()

        if cash_register_exist:
            await self.session.delete(cash_register_exist)
            await self.session.commit()

            return cash_register_exist
        return None

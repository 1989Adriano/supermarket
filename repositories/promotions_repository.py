from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.promotions_model import Promotions


class PromotionsRepository:
    """
    Repositório de Marketing e Encartes.
    Gerencia o agendamento de ofertas e preços promocionais, controlando
    as datas exatas de início e término das promoções nas gôndolas.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_promotions(self, data: dict) -> Promotions:
        """Recebe e Le o dicionário vindo da rota."""
        new_promotion = Promotions(**data)

        self.session.add(new_promotion)
        await self.session.commit()
        await self.session.refresh(new_promotion)

        return new_promotion

    # Read All
    async def get_all_promotions(self) -> list[Promotions]:
        result = await self.session.execute(select(Promotions))

        return result.scalars().all()

    # Read by ID
    async def get_promotions_by_id(self, promotion_id: int) -> Promotions | None:
        result = await self.session.execute(
            select(Promotions).where(Promotions.id == promotion_id)
        )

        # Se existe retorna ID, se não retorna None
        return result.scalar_one_or_none()

    # Update
    async def update_promotions(
        self, promotion_id: int, data: dict
    ) -> Promotions | None:

        result = await self.session.execute(
            select(Promotions).where(Promotions.id == promotion_id)
        )

        # Se existe cai no if, se não retorna None
        promotion_exist = result.scalar_one_or_none()

        if promotion_exist:
            for field, value in data.items():
                setattr(promotion_exist, field, value)

            await self.session.commit()
            await self.session.refresh(promotion_exist)

            return promotion_exist
        return None

    # Delete
    async def delete_promotion(self, promotion_id: int) -> Promotions | None:
        result = await self.session.execute(
            select(Promotions).where(Promotions.id == promotion_id)
        )

        # Se existe cai no if, se não retorna None
        promotion_exist = result.scalar_one_or_none()

        if promotion_exist:
            await self.session.delete(promotion_exist)
            await self.session.commit()

            return promotion_exist
        return None

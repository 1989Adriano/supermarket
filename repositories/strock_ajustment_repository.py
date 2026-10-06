from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.product_model import Products
from models.stock_adjustment_model import StockAdjustment


class StockAdjustmentRepository:
    """
    Repositório de Auditoria e Perdas de Estoque.
    Registra quebras, furtos ou vencimentos de mercadorias e, de 
    forma automatizada, aplica baixas negativas ou reajustes na 
    quantidade física atual do produto.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_stock_adjustment(self, data: dict) -> StockAdjustment:
        """Recebe e Le o dicionário vindo da rota."""
        new_stock = StockAdjustment(**data)

        # Busca o produto associado a esse ajuste direto no banco
        product_result = await self.session.execute(
            select(Products).where(Products.id == new_stock.product_id)
        )

        # Se existe cai no if, se não retorna None
        product_obj = product_result.scalar_one_or_none()

        if product_obj:
            # Perdas entram como negativo (ex: -3), fazer o '+=' vai subtrair o estoque.
            product_obj.stock_quantity += new_stock.quantity

        self.session.add(new_stock)
        await self.session.commit()
        await self.session.refresh(new_stock)

        return new_stock

    # Read All
    async def get_all_stock_adjustment(self) -> list[StockAdjustment]:
        result = await self.session.execute(select(StockAdjustment))

        return result.scalars().all()

    # Read by ID
    async def get_stock_adjustment_by_id(self, stock_id: int) -> StockAdjustment | None:
        result = await self.session.execute(
            select(StockAdjustment).where(StockAdjustment.id == stock_id)
        )

        return result.scalar_one_or_none()

    # Update
    async def update_stock_adjustment(
        self, stock_id: int, data: dict
    ) -> StockAdjustment | None:
        result = await self.session.execute(
            select(StockAdjustment).where(StockAdjustment.id == stock_id)
        )

        # Se existe cai no if, se não retorna None
        stock_exist = result.scalar_one_or_none()

        if stock_exist:
            for field, value in data.items():
                setattr(stock_exist, field, value)

            await self.session.commit()
            await self.session.refresh(stock_exist)

            return stock_exist
        return None

    # Delete
    async def delete_stock_adjustment(self, stock_id: int) -> StockAdjustment | None:
        result = await self.session.execute(
            select(StockAdjustment).where(StockAdjustment.id == stock_id)
        )

        # Se existe cai no if, se não retorna None
        stock_exist = result.scalar_one_or_none()

        if stock_exist:
            await self.session.delete(stock_exist)
            await self.session.commit()

            return stock_exist
        return None

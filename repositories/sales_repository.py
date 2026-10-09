from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.product_model import Products
from models.sale_model import SaleItem, Sales


#####################
# Sales
#####################
class SalesRepository:
    """
    Repositório do Ponto de Venda (PDV - Frente de Caixa).
    Orquestra o fechamento de cupons fiscais e carrinhos de compras
    em lote, vinculando itens vendidos e efetuando a baixa em tempo
    real no estoque de produtos.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_sale(self, sale_data: dict, items_data: list[dict]) -> Sales:
        """Recebe os dados do cupom e a lista de itens da rota para salvar em lote."""

        if items_data is None:
            items_data = []

        try:
            new_sale = Sales(**sale_data)
            self.session.add(new_sale)
            await self.session.flush()

            for item in items_data:
                item_obj = SaleItem(**item)
                item_obj.sale_id = new_sale.id  # Vincula o item ao ID do cupom

                product_result = await self.session.execute(
                    select(Products).where(Products.id == item_obj.product_id)
                )
                product_obj = product_result.scalar_one_or_none()

                if product_obj:
                    product_obj.stock_quantity -= item_obj.quantity

                self.session.add(item_obj)

            await self.session.commit()
            await self.session.refresh(new_sale)
            return new_sale

        except IntegrityError as e:
            await self.session.rollback()
            error_msg = str(e.orig).lower()

            # Status de Erro para se encontar erro de operador de caixa inexistente
            if "foreign key" in error_msg or "cashier_id" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Impossível abrir cupom! O ID do operador de caixa (cashier_id) informado não existe no sistema.",
                )

            # Status de Erro para se encontrar erro de número de cupom fiscal duplicado
            if "receipt_number" in error_msg or "unique" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um cupom fiscal registrado com este número de recebimento!",
                )

            # Tratamento genérico contra Erro 500
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de integridade de dados ao faturar a venda. Verifique as restrições.",
            )

    # Read All
    async def get_all_sales(self) -> list[Sales]:
        result = await self.session.execute(select(Sales))
        return list(result.scalars().all())

    # Read by ID
    async def get_sale_by_id(self, sale_id: int) -> Sales | None:
        result = await self.session.execute(select(Sales).where(Sales.id == sale_id))
        return result.scalar_one_or_none()

    # Update
    async def update_sale(self, sale_id: int, data: dict) -> Sales | None:
        result = await self.session.execute(select(Sales).where(Sales.id == sale_id))
        sale_exist = result.scalar_one_or_none()

        if sale_exist:
            for field, value in data.items():
                setattr(sale_exist, field, value)

            await self.session.commit()
            await self.session.refresh(sale_exist)

            return sale_exist
        return None

    # Delete
    async def delete_sale(self, sale_id: int) -> Sales | None:
        result = await self.session.execute(select(Sales).where(Sales.id == sale_id))
        sale_exist = result.scalar_one_or_none()

        if sale_exist:
            await self.session.delete(sale_exist)
            await self.session.commit()

            return sale_exist
        return None


#####################
# SaleItem
#####################
class SaleItemRepository:
    """
    Repositório de Detalhes de Vendas (Itens do Carrinho).
    Gerencia de forma isolada as operações de quantidade e preço cobrado
    para cada produto contido dentro de um cupom fiscal de venda.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_sale_item(self, data: dict) -> SaleItem:
        """Recebe e Le o dicionário vindo da rota."""
        try:
            new_sale = SaleItem(**data)

            result = await self.session.execute(
                select(Products).where(Products.id == new_sale.product_id)
            )

            # Se existe cai no if, se não retorna None
            product_obj = result.scalar_one_or_none()

            if product_obj:
                product_obj.stock_quantity -= new_sale.quantity

            self.session.add(new_sale)
            await self.session.commit()
            await self.session.refresh(new_sale)
            return new_sale

        except IntegrityError as e:
            await self.session.rollback()
            error_msg = str(e.orig).lower()

            # Status de Erro para se houver colisão de item único
            if "foreign key" in error_msg or "product_id" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não foi possível adicionar o item! O ID do produto informado não existe.",
                )

            # Tratamento genérico contra Erro 500
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de integridade de dados ao salvar o item da venda.",
            )

    # Read All
    async def get_all_sale_item(self) -> list[SaleItem]:
        result = await self.session.execute(select(SaleItem))
        return result.scalars().all()

    # Read by ID
    async def get_sale_item_by_id(self, sale_id: int) -> SaleItem | None:
        result = await self.session.execute(
            select(SaleItem).where(SaleItem.id == sale_id)
        )

        # Se existe retorna ID, se não retorna None
        return result.scalar_one_or_none()

    # Update
    async def update_sale_item(self, sale_id: int, data: dict) -> SaleItem | None:
        result = await self.session.execute(
            select(SaleItem).where(SaleItem.id == sale_id)
        )

        # Se existe cai no if, se não retorna None
        sale_item_exist = result.scalar_one_or_none()

        if sale_item_exist:
            for field, value in data.items():
                setattr(sale_item_exist, field, value)

            await self.session.commit()
            await self.session.refresh(sale_item_exist)

            return sale_item_exist
        return None

    # Delete
    async def delete_sate_item(self, sale_id: int) -> SaleItem | None:
        result = await self.session.execute(
            select(SaleItem).where(SaleItem.id == sale_id)
        )

        # Se existe cai no if, se não retorna None
        sale_item_exist = result.scalar_one_or_none()

        if sale_item_exist:
            await self.session.delete(sale_item_exist)
            await self.session.commit()

            return sale_item_exist
        return None

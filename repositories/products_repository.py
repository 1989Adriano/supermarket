from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.product_model import Products


class ProductsRepository:
    """
    Repositório de Catálogo de Produtos.
    Gerencia o cadastro comercial de mercadorias, códigos de barras,
    preços de gôndola e controle mínimo de estoque de segurança.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_product(self, data: dict) -> Products:
        """Recebe e Le o dicionário vindo da rota."""
        new_product = Products(**data)

        self.session.add(new_product)
        await self.session.commit()
        await self.session.refresh(new_product)

        return new_product

    # Read All
    async def get_all_products(self) -> list[Products]:
        result = await self.session.execute(select(Products))

        return list(result.scalars().all())

    # Read by ID
    async def get_products_by_id(self, products_id: int) -> Products | None:
        result = await self.session.execute(
            select(Products).where(Products.id == products_id)
        )

        # Se existe retorna ID, se não retorna None
        return result.scalar_one_or_none()

    # Update
    async def update_products(self, products_id: int, data: dict) -> Products | None:
        result = await self.session.execute(
            select(Products).where(Products.id == products_id)
        )

        # Se existe cai no if, se não retorna None
        products_exist = result.scalar_one_or_none()

        if products_exist:
            for field, value in data.items():
                setattr(products_exist, field, value)

            await self.session.commit()
            await self.session.refresh(products_exist)

            return products_exist
        return None

    # Delete
    async def delete_products(self, product_id: int) -> Products | None:
        result = await self.session.execute(
            select(Products).where(Products.id == product_id)
        )

        # Se existe cai no if, se não retorna None
        product_exist = result.scalar_one_or_none()

        if product_exist:
            await self.session.delete(product_exist)
            await self.session.commit()

            return product_exist
        return None

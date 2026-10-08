from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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
        try:
            new_product = Products(**data)

            self.session.add(new_product)
            await self.session.commit()
            await self.session.refresh(new_product)
            return new_product

        # Tratamento de erros
        except IntegrityError as e:
            await self.session.rollback()

            error_msg = str(e.orig).lower()

            # Status de Erro para Código de Barras duplicado
            if "code_bar" in error_msg or "barcode" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um produto cadastrado com este código de barras!",
                )

            # Status de Erro para Fornecedor que não existe no sistema (Chave Estrangeira)
            if "foreign key" in error_msg or "supplier_id" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O supplier_id fornecido não corresponde a nenhum fornecedor cadastrado!",
                )

            # Tratamento genérico de segurança para o banco
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de integridade de dados! Verifique os dados enviados.",
            )

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

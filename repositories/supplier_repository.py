from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.supplier_model import Supplier


class SupplierRepository:
    """
    Repositório de Fornecedores Comerciais.
    Gerencia as empresas parceiras que vendem mercadorias para o supermercado,
    controlando dados fiscais de CNPJ, Razão Social e contatos corporativos.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_supplier(self, data: dict) -> Supplier:
        """Recebe e Le o dicionário vindo da rota."""
        new_supplier = Supplier(**data)

        self.session.add(new_supplier)
        await self.session.commit()
        await self.session.refresh(new_supplier)

        return new_supplier

    # Read All
    async def get_all_supplier(self) -> list[Supplier]:
        result = await self.session.execute(select(Supplier))
        return list(result.scalars().all())

    # Read by ID
    async def get_supplier_by_id(self, supplier_id: int) -> Supplier | None:
        result = await self.session.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )

        # Se existe retorna ID, se não retorna None
        return result.scalar_one_or_none()

    # Update
    async def update_supplier(self, supplier_id: int, data: dict) -> Supplier | None:
        result = await self.session.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )

        # Se existe cai no if, se não retorna None
        supplier_exist = result.scalar_one_or_none()

        if supplier_exist:
            for field, value in data.items():
                setattr(supplier_exist, field, value)

            await self.session.commit()
            await self.session.refresh(supplier_exist)

            return supplier_exist
        return None

    # Delete
    async def delete_supplier(self, supplier_id: int) -> Supplier | None:
        result = await self.session.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )

        # Se existe cai no if, se não retorna None
        supplier_exist = result.scalar_one_or_none()

        if supplier_exist:
            await self.session.delete(supplier_exist)
            await self.session.commit()

            return supplier_exist
        return None

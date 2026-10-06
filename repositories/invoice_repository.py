from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.invoice_model import InvoiceItem, Invoices
from models.product_model import Products


######################
# InvoiceItem
######################
class InvoiceItemRepository:
    """
    Repositório de Detalhes de Compras (Itens da Nota).
    Gerencia de forma isolada os registros de quantidades e preços de custo
    negociados para cada produto contido em uma nota fiscal de faturamento.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_invoice_item(self, data: dict) -> InvoiceItem:
        """Recebe e Le o dicionário vindo da rota."""
        new_item = InvoiceItem(**data)

        # Busca o produto para aumentar o estoque.
        result = await self.session.execute(
            select(Products).where(Products.id == new_item.product_id)
        )
        product_obj = result.scalar_one_or_none()

        if product_obj:
            # SOMA o estoque, mercadoria está chegando do fornecedor.
            product_obj.stock_quantity += new_item.quantity

        self.session.add(new_item)
        await self.session.commit()
        await self.session.refresh(new_item)

        return new_item

    # Read All
    async def get_all_invoice_item(self) -> list[InvoiceItem]:
        result = await self.session.execute(select(InvoiceItem))

        return result.scalars().all()

    # Read by ID
    async def get_invoice_item_id(self, invoice_item_id: int) -> InvoiceItem | None:
        result = await self.session.execute(
            select(InvoiceItem).where(InvoiceItem.id == invoice_item_id)
        )

        # Se existe retorna ID, se não retorna None
        return result.scalar_one_or_none()

    # Update
    async def update_invice_item(
        self, invoice_item_id: int, data: dict
    ) -> InvoiceItem | None:
        result = await self.session.execute(
            select(InvoiceItem).where(InvoiceItem.id == invoice_item_id)
        )

        # Se existe cai no if, se não retorna None
        invoice_item_exist = result.scalar_one_or_none()

        if invoice_item_exist:
            for field, value in data.items():
                setattr(invoice_item_exist, field, value)

            await self.session.commit()
            await self.session.refresh(invoice_item_exist)

            return invoice_item_exist
        return None

    # Delete
    async def delete_invoice_item(self, invoice_item_id: int) -> InvoiceItem | None:
        result = await self.session.execute(
            select(InvoiceItem).where(InvoiceItem.id == invoice_item_id)
        )

        # Se existe cai no if, se não retorna None
        invoice_item_exist = result.scalar_one_or_none()

        if invoice_item_exist:
            await self.session.delete(invoice_item_exist)
            await self.session.commit()

            return invoice_item_exist
        return None


######################
# Invoice
######################
class InvoiceRepository:
    """
    Repositório de Lançamento de Notas Fiscais de Entrada (Compras).
    Orquestra o recebimento fiscal de cargas e faturamentos dos
    fornecedores em lote, vinculando itens comprados e efetuando a
    soma (abastecimento) em tempo real no estoque de produtos.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

        # Create

    async def create_invoice(
        self, invoice_data: dict, items_data: list[dict]
    ) -> Invoices:
        """Recebe os dados da nota e a lista de itens do lote para salvar em lote."""
        new_invoice = Invoices(**invoice_data)
        self.session.add(new_invoice)
        await self.session.flush()

        for item in items_data:
            item_obj = InvoiceItem(**item)
            item_obj.invoice_id = new_invoice.id

            # Busca o produto para abastecer a gôndola/depósito
            product_result = await self.session.execute(
                select(Products).where(Products.id == item_obj.product_id)
            )
            product_obj = product_result.scalar_one_or_none()

            if product_obj:
                # SOMA a quantidade da nota ao estoque real do produto
                product_obj.stock_quantity += item_obj.quantity

            self.session.add(item_obj)

        await self.session.commit()
        await self.session.refresh(new_invoice)

        return new_invoice

    # Read All
    async def get_all_invoices(self) -> list[Invoices]:
        result = await self.session.execute(select(Invoices))
        return list(result.scalars().all())

    # Read by ID
    async def get_invoice_by_id(self, invoice_id: int) -> Invoices | None:
        result = await self.session.execute(
            select(Invoices).where(Invoices.id == invoice_id)
        )

        return result.scalar_one_or_none()

    # Delete (Cancelamento ou estorno total da nota recebida)
    async def delete_invoice(self, invoice_id: int) -> Invoices | None:
        result = await self.session.execute(
            select(Invoices).where(Invoices.id == invoice_id)
        )
        invoice_exist = result.scalar_one_or_none()

        if invoice_exist:
            await self.session.delete(invoice_exist)
            await self.session.commit()

            return invoice_exist
        return None

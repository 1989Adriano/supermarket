from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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
        try:
            new_item = InvoiceItem(**data)

            # Busca o produto para aumentar o estoque.
            result = await self.session.execute(
                select(Products).where(Products.id == new_item.product_id)
            )
            product_obj = result.scalar_one_or_none()

            # Garante que o produto existe antes de abastecer
            if not product_obj:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não foi possível adicionar o item! O ID do produto informado não existe no sistema.",
                )

            # SOMA o estoque, mercadoria está chegando do fornecedor.
            product_obj.stock_quantity += new_item.quantity

            self.session.add(new_item)
            await self.session.commit()
            await self.session.refresh(new_item)
            return new_item

        except IntegrityError as e:
            await self.session.rollback()
            error_msg = str(e.orig).lower()

            # Status de Erro para se houver colisão de dados unicos
            if "foreign key" in error_msg and "invoice" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Erro de amarração fiscal! O ID da nota fiscal (invoice_id) informado não existe.",
                )

            # Tratamento genérico de segurança generico Erro 500
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de integridade referencial ao salvar o item da nota.",
            )

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
        try:
            new_invoice = Invoices(**invoice_data)
            self.session.add(new_invoice)
            await self.session.flush()

            for item in items_data:
                item_dict = (
                    item.model_dump() if hasattr(item, "model_dump") else dict(item)
                )
                item_obj = InvoiceItem(**item_dict)
                item_obj.invoice_id = new_invoice.id

                # Busca o produto para abastecer a gôndola/depósito
                product_result = await self.session.execute(
                    select(Products).where(Products.id == item_obj.product_id)
                )
                product_obj = product_result.scalar_one_or_none()

                # Cancela todo o lote se um único produto for fantasma/falso
                if not product_obj:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Lançamento cancelado! O produto ID {item_obj.product_id} inserido na lista de itens não existe no sistema.",
                    )

                # SOMA a quantidade da nota ao estoque real do produto
                product_obj.stock_quantity += item_obj.quantity

                self.session.add(item_obj)

            await self.session.commit()
            await self.session.refresh(new_invoice)
            return new_invoice

        except IntegrityError as e:
            await self.session.rollback()
            error_msg = str(e.orig).lower()

            # Verifica o fornecedor fantasma
            if "foreign key" in error_msg and "supplier" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não foi possível emitir a nota! O ID do fornecedor (supplier_id) informado não existe no sistema.",
                )

            # Verifica e captura o numero da nota errado/fantasma
            if "unique constraint" in error_msg or "invoice_number" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Conflito fiscal! Uma Nota Fiscal com este mesmo número (invoice_number) já está lançada no sistema.",
                )

            # Tratamento genérico de segurança generico Erro 500
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de consistência ao salvar cabeçalho e itens da nota fiscal de entrada.",
            )

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

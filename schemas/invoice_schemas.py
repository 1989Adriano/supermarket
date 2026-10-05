from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from schemas.product_schemas import ProductResponse
from schemas.supplier_schemas import SupplierResponse


# =========================
# CLASSE BASE INVOICE ITEM
# =========================
class BaseInvoiceItem(BaseModel):
    """Campos obrigatórios de cada produto inserido dentro de uma Nota Fiscal de Entrada"""

    quantity: int = Field(..., gt=0)  # Quantidade comprada do produto

    # Preço de custo pago por unidade
    unit_cost: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)

    invoice_id: int  # Relação com a Nota Fiscal
    product_id: int  # Relação com o Produto (classe Products)


class InvoiceItemRequest(BaseInvoiceItem):
    pass


class InvoiceItemResponse(BaseInvoiceItem):
    """Retorna o item comprado com seu ID e os dados completos do produto"""

    id: int

    # Relacionamento com Products
    product: ProductResponse | None = None

    # Config: ler os objetos do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class InvoiceItemUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=0)
    unit_cost: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    invoice_id: int | None = None
    product_id: int | None = None


# =====================
# CLASSE BASE INVOICES
# =====================
class BaseInvoices(BaseModel):
    """Dados gerais fiscais e de cabeçalho da Nota Fiscal de Entrada"""

    # Número da NF-e (ex: 000.123.456)
    invoice_number: str = Field(..., min_length=5, max_length=20)
    series: str | None = Field(default=None, max_length=5)  # Série da nota (ex: 1)

    # Quando chegou no mercado
    received_at: datetime = Field(default_factory=datetime.now)

    # Valor total da nota (R$)
    total_amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    supplier_id: int


class InvoicesRequest(BaseInvoices):
    """
    Quando o almoxarifado lança uma nota, envia o cabeçalho
    e a lista de produtos comprados tudo junto.
    """

    items: list[InvoiceItemRequest] = Field(..., min_items=1)


class InvoicesResponse(BaseInvoices):
    """Retorna a Nota Fiscal de Entrada completa com fornecedor e produtos integrados"""

    id: int
    received_at: datetime
    issue_date: datetime | None = None

    # Relacionamento com supplier
    supplier: SupplierResponse | None = None

    # Relacionamento com o Fornecedor
    items: list[InvoiceItemResponse] = []

    # Config: ler os objetos do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class InvoicesUpdate(BaseModel):
    invoice_number: str | None = Field(default=None, min_length=5, max_length=20)
    series: str | None = Field(default=None, max_length=5)
    received_at: datetime | None = Field(default=None)
    total_amount: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    supplier_id: int | None = None

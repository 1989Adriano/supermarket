from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.sale_model import EnumPaymentMethod


# ==============================
# ITENS DO CARRINHO (SALE ITEM)
# ==============================
class BaseSaleItem(BaseModel):
    """Campos obrigatórios de um produto inserido no carrinho de compras"""

    quantity: int = Field(..., gt=0, description="Quantidade de unidades vendidas")

    unit_price: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Preço unitário cobrado no caixa",
    )

    sale_id: int
    product_id: int


class SaleItemRequest(BaseSaleItem):
    pass


class SaleItemResponse(BaseSaleItem):
    id: int

    # Config: ler os objetos do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class SaleItemUpdate(BaseModel):
    quantity: int | None = Field(default=None, gt=0)

    unit_price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )

    sale_id: int | None = Field(default=None)
    product_id: int | None = Field(default=None)


# =====================================
# CUPOM FISCAL DE VENDA (SALES MESTRE)
# =====================================
class BaseSales(BaseModel):
    """Dados gerais do cabeçalho de uma venda no Ponto de Venda (PDV)"""

    receipt_number: str | None = Field(default=None, min_length=3, max_length=50)
    created_at: datetime = Field(default_factory=datetime.now)
    subtotal: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    discount: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    total_amount: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    payment_method: EnumPaymentMethod = Field(default=EnumPaymentMethod.CASH)
    client_cpf: str | None = Field(default=None, min_length=14, max_length=14)
    cashier_id: int


class SalesRequest(BaseSales):
    pass


class SalesResponse(BaseSales):
    id: int

    # Relação com Model Sales
    items: list[SaleItemResponse] = []

    # Config: ler os objetos do SQLAlchemy usando ponto
    model_config = ConfigDict(from_attributes=True)


class SalesUpdate(BaseModel):
    receipt_number: str | None = Field(default=None, min_length=3, max_length=50)
    created_at: datetime | None = None

    subtotal: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )

    discount: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )

    total_amount: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )

    payment_method: EnumPaymentMethod | None = None
    client_cpf: str | None = Field(default=None, min_length=14, max_length=14)
    cashier_id: int | None = None

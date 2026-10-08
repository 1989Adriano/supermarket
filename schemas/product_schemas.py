from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.product_model import EnumCategory, EnumUnitType
from schemas.supplier_schemas import SupplierResponse


class BaseProduct(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    brand: str = Field(..., min_length=3, max_length=100)  # marca
    code_bar: str = Field(..., min_length=5, max_length=20)
    stock_quantity: int = Field(default=0, ge=0)
    min_stock: int = Field(default=5, ge=0)
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)

    cost_price: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )

    category: EnumCategory = Field(default=EnumCategory.VARIATED)
    unit_type: EnumUnitType = Field(default=EnumUnitType.UNIT)
    is_perishable: bool = Field(default=False)
    expiration_date: date | None = Field(default=None)
    ncm_code: str | None = Field(default=None, min_length=3, max_length=8)

    supplier_id: int | None = Field(
        default=None, description="ID numérico do fornecedor"
    )


class ProductRequest(BaseProduct):
    pass


class ProductResponse(BaseProduct):
    id: int

    # Relacionamento com Supplier
    supplier: SupplierResponse | None = None

    # Config: ler os objetos do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class ProductUpate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=150)
    brand: str | None = Field(default=None, min_length=3, max_length=100)  # marca
    code_bar: str | None = Field(default=None, min_length=5, max_length=20)
    stock_quantity: int | None = Field(default=None, ge=0)

    min_stock: int | None = Field(
        default=None,
        ge=0,
    )

    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)

    cost_price: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )

    category: EnumCategory | None = None
    unit_type: EnumUnitType | None = None
    is_perishable: bool | None = None
    expiration_date: date | None = Field(default=None)
    ncm_code: str | None = Field(default=None, min_length=3, max_length=8)
    supplier_id: int | None = Field(default=None)

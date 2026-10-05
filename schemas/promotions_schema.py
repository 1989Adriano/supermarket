from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BasePromotions(BaseModel):
    """Classe que cria uma promoção com data inicial e fim."""

    name: str
    promotional_price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    start_date: datetime
    end_date: datetime
    is_active: bool | None = Field(default=True)
    product_id: int


class PromotionsRequest(BasePromotions):
    pass


class PromotionsResponse(BasePromotions):
    id: int

    # Config: ler os objetos do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class PromotionsUpdate(BaseModel):
    name: str | None = Field(default=None)

    promotional_price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )

    start_date: datetime | None = Field(default=None)
    end_date: datetime | None = Field(default=None)
    is_active: bool | None = None
    product_id: int | None = None

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.stock_adjustment_model import EnumReason


class BaseStockAdjustment(BaseModel):
    quantity: int
    adjusted_at: datetime = Field(default_factory=datetime.now)
    reason: EnumReason = Field(default=EnumReason.INTERNAL_CONSUMPTION)
    notes: str | None = Field(default=None, min_length=3, max_length=255)
    product_id: int
    employee_id: int


class StockAdjustmentRequest(BaseStockAdjustment):
    pass


class StockAdjustmentResponse(BaseStockAdjustment):
    id: int

    # Config: ler os objetos do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class StockAdjustmentUpdate(BaseModel):
    quantity: int | None = Field(default=None)
    adjusted_at: datetime | None = Field(default=None)
    reason: EnumReason | None = None
    notes: str | None = Field(default=None, min_length=3, max_length=255)
    product_id: int | None = None
    employee_id: int | None = None

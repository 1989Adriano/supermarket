from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BaseCashRegister(BaseModel):
    """Contém os campos que o funcionário ativa ao abrir e fechar o caixa"""

    terminal_number: str = Field(..., min_length=3, max_length=10)
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: datetime | None = Field(default=None)
    opening_balance: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)

    closing_balance: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )

    status: str = Field(..., min_length=3, max_length=20)
    cashier_id: int


class CashRegisterRequest(BaseCashRegister):
    pass


class CashRegisterResponse(BaseCashRegister):
    id: int

    # Config
    model_config = ConfigDict(from_attributes=True)


class CashRegisterUpdate(BaseModel):
    terminal_number: str | None = Field(default=None, min_length=3, max_length=10)
    opened_at: datetime | None = None
    closed_at: datetime | None = Field(default=None)

    opening_balance: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )

    closing_balance: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    
    status: str | None = Field(default=None, min_length=3, max_length=20)
    cashier_id: int | None = None

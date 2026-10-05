from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.payments_model import EnumTransactionStatus


class BasePayments(BaseModel):
    amount: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    transaction_date: datetime = Field(default_factory=datetime.now)

    # Ex: 'Stone', 'Cielo', 'Banco do Brasil'   
    acquirer: str | None = Field(default=None,  min_length=3, max_length=50)

    # Código NSU do comprovante do cartão    
    authorization_code: str| None = Field(default=None, min_length=3, max_length=50)
    
    status: EnumTransactionStatus = Field(default=EnumTransactionStatus.APPROVED)   
    sale_id: int


class PaymentRequest(BasePayments):
    pass


class PaymentResponse(PaymentRequest):
    id: int

    # Config: ler os objetos do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class PaymentUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    transaction_date: datetime | None = Field(default=None)    
    acquirer: str | None = Field(default=None, min_length=3, max_length=50)
    authorization_code: str | None = Field(default=None, min_length=3, max_length=50)  
    status: EnumTransactionStatus | None = None 
    sale_id: int | None = None

from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy import Enum as SQLEnum

from core.database import Base


class EnumTransactionStatus(str, Enum):
    """
    Define os estados possíveis para uma transação financeira de cartão ou Pix.
    """

    APPROVED = "aprovada"
    CANCELED = "cancelada"
    REFUNDED = "estornada"
    PENDING = "pendente"


class PaymentTransactions(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_date = Column(DateTime, default=func.now(), nullable=False)

    # Dados da maquininha / banco Ex: 'Stone', 'Cielo', 'Banco do Brasil'
    acquirer = Column(String(50), nullable=True)

    # Código NSU do comprovante do cartão
    authorization_code = Column(String(50), nullable=True)

    # Status da maquininha
    status = Column(
        SQLEnum(EnumTransactionStatus, native_enum=False),
        default=EnumTransactionStatus.APPROVED,
        nullable=False,
    )

    # Relação com cupom de venda veio essa transação
    sale_id = Column(
        Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False
    )

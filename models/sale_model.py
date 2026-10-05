from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from core.database import Base


class EnumPaymentMethod(str, Enum):
    """
    Define as formas de pagamento permitidas no caixa do supermercado.
    """

    CASH = "dinheiro"
    CREDIT_CARD = "cartao_credito"
    DEBIT_CARD = "cartao_debito"
    PIX = "pix"
    FOOD_STAMP = "vale_alimentacao"


class Sales(Base):
    """
    Guarda os dados gerais do cupom fiscal / venda realizada no caixa.
    """

    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    receipt_number = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Valores de fechamento do cupom
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)

    # Aplicando o seu Enum com segurança
    payment_method = Column(
        SQLEnum(EnumPaymentMethod, native_enum=False),
        default=EnumPaymentMethod.CASH,
        nullable=False,
    )

    client_cpf = Column(String(14), nullable=True)

    # Vincula qual funcionário realizou a venda (Operador de Caixa)
    cashier_id = Column(
        Integer, ForeignKey("employee.id", ondelete="RESTRICT"), nullable=False
    )
    cashier = relationship("Employee", lazy="joined")

    # Lista automática dos itens contidos nesta venda
    items = relationship(
        "SaleItem", back_populates="sale", lazy="selectin", cascade="all, delete-orphan"
    )


class SaleItem(Base):
    """
    Tabela Detalhe: Guarda cada produto que o cliente passou no caixa, quantidade e preço.
    """

    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)  # Quantidade comprada (ou peso em KG)
    unit_price = Column(
        Numeric(10, 2), nullable=False
    )  # Preço cobrado por unidade no momento da venda

    # Relação com a Venda Geral(Cupom)
    sale_id = Column(
        Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False
    )
    sale = relationship("Sale", back_populates="items")

    # Relação com o Produto Vendido
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    product = relationship("Products", lazy="joined")

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from core.database import Base


class Invoices(Base):
    """
    Guarda os dados gerais da Nota Fiscal enviada pelo Fornecedor.
    """

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)

    invoice_number = Column(
        String(20), unique=True, nullable=False
    )  # Número da NF-e (ex: 000.123.456)

    series = Column(String(5), nullable=True)  # Série da nota (ex: 1)
    issue_date = Column(DateTime, nullable=False)  # Data de emissão da nota

    received_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )  # Quando chegou no mercado

    total_amount = Column(Numeric(10, 2), nullable=False)  # Valor total da nota (R$)

    # Relacionamento com o Fornecedor
    supplier_id = Column(
        Integer, ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False
    )
    supplier = relationship("Supplier", lazy="joined")

    # Relacionamento com os itens(supplier.py) (Gera uma lista automática)
    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class InvoiceItem(Base):
    """
    Guarda cada produto comprado dentro da Nota Fiscal.
    """

    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)

    # Preço de custo pago por unidade
    unit_cost = Column(Numeric(10, 2), nullable=False)

    # Relação com a Nota Fiscal
    invoice_id = Column(
        Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False
    )
    invoice = relationship("Invoice", back_populates="items")

    # Relação com o Produto (classe Products)
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    product = relationship("Products", lazy="joined")

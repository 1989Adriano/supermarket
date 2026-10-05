# Sugestão de Model para o arquivo promotions.py
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String

from core.database import Base


class Promotions(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # Ex: "Encarte de Aniversário"
    promotional_price = Column(Numeric(10, 2), nullable=False)  # Preço com desconto

    # Validade automática da oferta.
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relação com o produto está na promoção.
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )

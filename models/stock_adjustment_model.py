# Sugestão de Model para o arquivo stock_adjustment.py
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SQLEnum

from core.database import Base


class EnumReason(str, Enum):
    """
    Define os motivos para ajuste manual de estoque no supermercado.
    Fundamental para auditoria de perdas (quebras, vencimentos e inventário).
    """

    EXPIRATION = "vencimento"
    DAMAGE = "quebra_avaria"
    THEFT = "furto_roubo"
    PRODUCE_WASTE = "descarte_hortifruti"
    INVENTORY_AUDIT = "inventario"
    INTERNAL_CONSUMPTION = "consumo_interno"
    SUPPLIER_RETURN = "devolucao_fornecedor"


class StockAdjustment(Base):
    """
    Classe que registra qualquer alteração manual no estoque do supermercado.
    """

    __tablename__ = "stock_adjustments"

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    adjusted_at = Column(DateTime, default=func.now(), nullable=False)

    # Causa/Ocorrido com produto perdido
    reason = Column(SQLEnum(EnumReason, native_enum=False), nullable=False)
    notes = Column(String(255), nullable=True)  # Observações livres do gerente

    # Relacionamentos Produtos e Funcionario
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )

    employee_id = Column(
        Integer, ForeignKey("employee.id", ondelete="RESTRICT"), nullable=False
    )

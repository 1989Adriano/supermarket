# Sugestão de Model para o arquivo cash_register.py
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func

from core.database import Base


class CashRegisterSession(Base):
    """Caixa do supermercado"""

    __tablename__ = "cash_register_sessions"

    id = Column(Integer, primary_key=True)
    terminal_number = Column(String(10), nullable=False)  # Ex: "Caixa 01"
    opened_at = Column(DateTime, default=func.now(), nullable=False)

    # Fica nulo enquanto o caixa trabalhar
    closed_at = Column(DateTime, nullable=True)

    # Dinheiro de troco inicial
    opening_balance = Column(Numeric(10, 2), nullable=False)

    # Quanto tinha no fim do turno
    closing_balance = Column(Numeric(10, 2), nullable=True)

    # 'Aberto' ou 'Fechado'
    status = Column(String(20), default="Aberto", nullable=False)

    # Relação com o funcionário que abriu aquele caixa específico.
    cashier_id = Column(Integer, ForeignKey("employee.id"), nullable=False)

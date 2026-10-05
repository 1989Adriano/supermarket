# Sugestão de Model para o arquivo cash_register.py
import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from core.database import Base


class CashRegisterSession(Base):
    """Caixa do supermercado"""

    __tablename__ = "cash_register_sessions"

    id = Column(Integer, primary_key=True)
    terminal_number = Column(String(10), nullable=False)  # Ex: "Caixa 01"
    opened_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    closed_at = Column(DateTime, nullable=True)  # Fica nulo enquanto o caixa trabalhar

    # Valores Fiscal/Financeira
    opening_balance = Column(
        Numeric(10, 2), nullable=False
    )  # Dinheiro de troco inicial
    closing_balance = Column(
        Numeric(10, 2), nullable=True
    )  # Quanto tinha no fim do turno

    status = Column(
        String(20), default="Aberto", nullable=False
    )  # 'Aberto' ou 'Fechado'

    # Relação com o funcionário que abriu aquele caixa específico.
    cashier_id = Column(Integer, ForeignKey("employee.id"), nullable=False)

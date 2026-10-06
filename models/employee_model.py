from enum import Enum

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from models.class_mother_personnel_model import BaseComplement, BaseFile


class EnumRoleTitle(str, Enum):
    """ "
    Classe que lista os cargos do supermercado.
    """

    STORE_MANAGER = "gerente"
    ASSISTANT_STORE_MANAGER = "subgerente"
    CASHIER = "operador_caixa"
    CHECkOUT_SUPERVISOR = "fiscal_caixa"
    BAGGER = "empacotador"
    LOSS_OFFICER = "fiscal_perdas"
    SECURITY_GUARD = "segurança"
    STOCK_CLERK = "repositor_mercadorias"
    INVENTORY_CLERK = "conferente_estoquista"
    SIGN_WRITER = "cartazista"
    BUTCHER = "acougueiro"
    BAKER = "padeiro"
    DELI_COUNTER_WORKER = "balconista_frios"
    PRODUCE_CLERK = "auxiliar_hortifruti"


class EmployeeComplements(BaseComplement):
    __tablename__ = "employee_complements"


class Employee(BaseFile):
    __tablename__ = "employee"

    # Relaçao com o complemento
    complement_id = Column(
        Integer,
        ForeignKey("employee_complements.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    complement = relationship("EmployeeComplements", lazy="joined")

    # Dados de Carteira do Funcionario
    pis_pasep = Column(String(11), unique=True, nullable=False)
    
    ctps_number = Column(String(20), nullable=False)
    admission_date = Column(Date, nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)

    # Cargo Funcinario
    role_title = Column(
        SQLEnum(EnumRoleTitle, native_enum=False),
        default=EnumRoleTitle.BAGGER,
        nullable=False,
    )

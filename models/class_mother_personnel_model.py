from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)

from core.database import Base


class EnumSex(str, Enum):
    MAN = "M"
    WOMAN = "F"
    OTHER = "O"
    EMPTY = "E"


class BaseFile(Base):
    """
    Classe abstrata com dados principais dos Cadastros.
    As tabelas filhas (User, Employee) herdarão estes campos.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)

    # Endereço Principal
    address_line_1 = Column(String(255), nullable=False)
    city = Column(String(150), nullable=True)
    neighborhood = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)

    # Documentos e Contato
    email = Column(String(100), unique=True, nullable=False)
    cpf = Column(String(13), unique=True, nullable=False)
    birthday = Column(Date, nullable=False)
    phone1 = Column(String(20), nullable=False)

    # Controle de Sistema
    is_active = Column(Boolean, default=True, nullable=False)
    date_acc_created = Column(DateTime, default=func.datetime.now(), nullable=False)


class BaseComplement(Base):
    """
    Classe abstrata com os dados complementares do Cadastro.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    age = Column(Integer, nullable=True)
    postal_code = Column(String(20), nullable=True)
    father_name = Column(String(150), nullable=True)
    mother_name = Column(String(150), nullable=True)
    tphone2 = Column(String(20), nullable=True)
    profession = Column(String(100), nullable=True)
    married = Column(Boolean, default=False)
    coments = Column(String(250), nullable=True)

    sex = Column(
        SQLEnum(EnumSex, native_enum=False), default=EnumSex.EMPTY, nullable=True
    )
    
    rg = Column(String(20), unique=True, nullable=True)
    nationality = Column(String(50), nullable=True)
    place_of_birth = Column(String(50), nullable=True)

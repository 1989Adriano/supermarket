from sqlalchemy import Boolean, Column, Integer, String

from core.database import Base


class Supplier(Base):
    """
    Classe que guarda os dados dos fornecedores/vendedores
    que vendem mercadorias PARA o supermercado.
    """

    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)

    # Razão Social
    corporate_name = Column(String(150), nullable=False)

    # Nome Fantasia
    trade_name = Column(String(150), nullable=False)

    # Ex: 00.000.000/0000-00
    cnpj = Column(String(18), unique=True, nullable=False) 

    # Inscrição Estadual (IE)
    state_registration = Column(String(20), unique=True, nullable=True)
   
    # Nome do vendedor que te atende
    contact_name = Column(String(100), nullable=False) 
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=False)

    # Endereço da Distribuidora/Fábrica
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

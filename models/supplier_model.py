from sqlalchemy import Column, String, Integer, Boolean
from core.database import Base


class Supplier(Base):
    """
    Classe que guarda os dados dos fornecedores/vendedores 
    que vendem mercadorias PARA o supermercado.
    """
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True)
    corporate_name = Column(String(150), nullable=False) # Razão Social
    trade_name = Column(String(150), nullable=False)     # Nome Fantasia
    
    # Documentos Fiscais
    cnpj = Column(String(18), unique=True, nullable=False)               # Ex: 00.000.000/0000-00
    state_registration = Column(String(20), unique=True, nullable=True) # Inscrição Estadual (IE)

    # Contato do Vendedor/Representante Comercial
    contact_name = Column(String(100), nullable=False) # Nome do vendedor que te atende
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=False)
    
    # Endereço da Distribuidora/Fábrica
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    
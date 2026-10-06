from enum import Enum

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SQLEnum

from core.database import Base


class EnumCategory(str, Enum):
    """
    Classe que lista as categorias de produtos de um supermercado.
    """

    GROCERY = "mercearia"
    BEVERAGES = "bebidas"
    BAKERY = "padaria"
    BUTCHERY = "acougue"
    SEAFOOD = "peixaria"
    DAIRY_EGGS = "laticinios_ovos"
    PRODUCE = "hortifruti"
    FROZEN_FOODS = "congelados"
    CLEANING_SUPPLIES = "limpeza"
    PERSONAL_CARE = "higiene_pessoal"
    PET_SHOP = "pet_shop"
    HOUSEWARES = "utilidades_domesticas"
    VARIATED = "variados"


class EnumUnitType(str, Enum):
    """
    Define como o produto é vendido (Unidade, Quilo, Litro)
    """

    UNIT = "UN"
    KILOGRAM = "KG"
    LITER = "LT"


class Products(Base):
    """
    Classe que guarda todos os dados de um produto
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    brand = Column(String(100), nullable=False)  # marca
    code_bar = Column(String(20), unique=True, nullable=False)

    # Controle de Estoque
    stock_quantity = Column(Integer, default=0, nullable=False)
    min_stock = Column(Integer, default=5, nullable=False)

    # Preços e Margem
    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=True)

    # Regras e Classificações
    category = Column(SQLEnum(EnumCategory, native_enum=False), nullable=False)
    unit_type = Column(
        SQLEnum(EnumUnitType, native_enum=False),
        default=EnumUnitType.UNIT,
        nullable=False,
    )
    
    is_perishable = Column(Boolean, default=False, nullable=False)
    expiration_date = Column(Date, nullable=True)

    # Campo Fiscal no Brasil (NFC-e)
    ncm_code = Column(String(8), nullable=True)

    # Realação com Vendedores de Produtos
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BaseSupplier(BaseModel):
    """Cadastro do Fornecedor/Vendedor"""

    corporate_name: str = Field(..., min_length=5, max_length=150)
    trade_name: str = Field(..., min_length=5, max_length=150)
    cnpj: str = Field(..., min_length=18, max_length=18)
    contact_name: str = Field(..., min_length=5, max_length=100)
    email: EmailStr = Field(..., max_length=100)
    phone: str = Field(..., min_length=5, max_length=20)
    is_active: bool = Field(default=True)
    state_registration: str | None = Field(default=None, min_length=5, max_length=20)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=255)
    state: str | None = Field(default=None, min_length=2, max_length=2)


class SupplierRequest(BaseSupplier):
    pass


class SupplierResponse(BaseSupplier):
    id: int

    # Config: ler os objetos do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class SupplierUpdate(BaseModel):
    corporate_name: str | None = Field(default=None, min_length=5, max_length=150)
    trade_name: str | None = Field(default=None, min_length=5, max_length=150)
    cnpj: str | None = Field(default=None, min_length=18, max_length=18)
    state_registration: str | None = Field(default=None, min_length=5, max_length=20)
    contact_name: str | None = Field(default=None, min_length=5, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, min_length=5, max_length=20)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=255)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    is_active: bool | None = None

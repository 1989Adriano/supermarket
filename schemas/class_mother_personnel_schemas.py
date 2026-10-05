from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.class_mother_personnel_model import EnumSex


# ===========================================
# SCHEMAS DOS DADOS PRINCIPAIS (BASE MOTHER)
# ===========================================
class BaseMotherSchema(BaseModel):
    """Contém os campos que o usuário deve enviar no cadastro"""

    first_name: str = Field(..., min_length=3, max_length=50)
    middle_name: str | None = Field(default=None, min_length=3, max_length=100)
    last_name: str = Field(..., min_length=3, max_length=100)
    address_line_1: str = Field(..., min_length=3, max_length=255)
    city: str | None = Field(default=None, min_length=3, max_length=50)
    neighborhood: str = Field(..., min_length=3, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)  # trava com 2 digitos
    email: EmailStr = Field(..., max_length=100)
    cpf: str = Field(..., min_length=11, max_length=14)
    birthday: date
    phone1: str = Field(..., min_length=3, max_length=20)
    is_active: bool = Field(default=True)


class MotherRequest(BaseMotherSchema):
    pass


class MotherResponse(BaseMotherSchema):
    id: int
    date_acc_created: datetime

    # Config: ler os objetos do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class MotherUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=3, max_length=50)
    middle_name: str | None = Field(default=None, min_length=3, max_length=100)
    last_name: str | None = Field(default=None, min_length=3, max_length=100)
    address_line_1: str | None = Field(default=None, min_length=3, max_length=255)
    city: str | None = Field(default=None, min_length=3, max_length=150)
    neighborhood: str | None = Field(default=None, min_length=3, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    email: EmailStr | None = Field(default=None, max_length=100)
    cpf: str | None = Field(default=None, min_length=11, max_length=14)
    birthday: date | None = None
    phone1: str | None = Field(default=None, min_length=3, max_length=20)
    is_active: bool | None = None


# ===================================================
# SCHEMAS DOS DADOS COMPLEMENTARES (BASE COMPLEMENT)
# ===================================================
class BaseComplementSchema(BaseModel):
    age: int | None = Field(default=None, ge=0, le=120)
    postal_code: str | None = Field(default=None, min_length=3, max_length=20)
    father_name: str | None = Field(default=None, min_length=3, max_length=150)
    mother_name: str | None = Field(default=None, min_length=3, max_length=150)
    phone2: str | None = Field(default=None, min_length=3, max_length=20)
    profession: str | None = Field(default=None, min_length=3, max_length=100)
    married: bool = Field(default=False)
    coments: str | None = Field(default=None, min_length=3, max_length=250)
    sex: EnumSex | None = Field(default=EnumSex.EMPTY)
    rg: str | None = Field(default=None, min_length=3, max_length=20)
    nationality: str | None = Field(default=None, min_length=3, max_length=50)
    place_of_birth: str | None = Field(default=None, min_length=3, max_length=50)


class ComplementRequest(BaseComplementSchema):
    """Usado na criação do complemento"""

    pass


class ComplementResponse(BaseComplementSchema):
    """Recebe os dados do BaseSupplier, e complemneta com seu proprio atributo"""

    id: int

    # Config: ler os objetos do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class ComplementUpdate(BaseModel):
    """Campos de atualização do complemento (Todos Opcionais)"""

    age: int | None = Field(default=None, ge=0, le=120)
    postal_code: str | None = Field(default=None, min_length=3, max_length=20)
    father_name: str | None = Field(default=None, min_length=3, max_length=150)
    mother_name: str | None = Field(default=None, min_length=3, max_length=150)
    phone2: str | None = Field(default=None, min_length=3, max_length=20)
    profession: str | None = Field(default=None, min_length=3, max_length=100)
    married: bool | None = None
    coments: str | None = Field(default=None, min_length=3, max_length=250)
    sex: EnumSex | None = None
    rg: str | None = Field(default=None, min_length=3, max_length=20)
    nationality: str | None = Field(default=None, min_length=3, max_length=50)
    place_of_birth: str | None = Field(default=None, min_length=3, max_length=50)

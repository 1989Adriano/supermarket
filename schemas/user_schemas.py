from datetime import datetime

from pydantic import BaseModel, Field

from schemas.class_mother_personnel_schemas import (
    BaseMotherSchema,
    ComplementResponse,
    MotherResponse,
    MotherUpdate,
)


class UserRequest(BaseMotherSchema):
    """Recebe os dados de cadastro do usuário."""

    complement_id: int | None = Field(
        default=None, description="ID do complemento do usuário previamente cadastrado"
    )
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: str = Field(default="user", min_length=3, max_length=50)


class UserLoginRequest(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(MotherResponse):
    last_date_login: datetime | None = None
    role: str = "user"

    # Relacionamento Estrangeiro completo
    complement_id: int | None = None
    complement: ComplementResponse | None = None


class UserUpdate(MotherUpdate):
    last_date_login: datetime | None = Field(default=None)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: str | None = Field(default=None, min_length=3, max_length=50)

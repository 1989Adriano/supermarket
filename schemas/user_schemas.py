from datetime import datetime

from pydantic import Field

from schemas.class_mother_personnel_schemas import (
    BaseMotherSchema,
    ComplementResponse,
    MotherResponse,
    MotherUpdate,
)


class UserRequest(BaseMotherSchema):
    """
    Recebe os dados da classe mãe(cadastro) para criar um novo usuário no sistema.
    """

    complement_id: int | None = Field(
        ..., description="ID do complemento do usuário previamente cadastrado"
    )


class UserResponse(MotherResponse):
    last_date_login: datetime | None = None

    # Relacionamento Estrangeiro completo
    complement_id: int | None = None
    complement: ComplementResponse | None = None


class UserUpdate(MotherUpdate):
    last_date_login: datetime | None = Field(default=None)

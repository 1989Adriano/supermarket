from datetime import date
from decimal import Decimal

from pydantic import Field

from models.employee_model import EnumRoleTitle
from schemas.class_mother_personnel_schemas import (
    BaseMotherSchema,
    ComplementResponse,
    MotherRequest,
    MotherResponse,
    MotherUpdate,
)


class BaseEmployeeRequest(BaseMotherSchema):
    """Recebe os dados cadastrais do funcionario.
    Que vem da Classe mãe, e adiona os dados
    que estão nessa classe.
    """

    complement_id: int | None = Field(
        default=None, description="ID do complemento do usuário previamente cadastrado"
    )

    pis_pasep: str = Field(
        ..., min_length=11, max_length=11, description="PIS/PASEP apenas com números"
    )

    ctps_number: str = Field(..., max_length=20)
    admission_date: date
    salary: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    role_title: EnumRoleTitle = Field(default=EnumRoleTitle.BAGGER)


class EmployeeRequest(BaseEmployeeRequest):
    pass


class EmployeeResponse(MotherResponse):
    pis_pasep: str
    ctps_number: str
    admission_date: date
    salary: Decimal
    role_title: EnumRoleTitle

    # Relacionamento o a tabela Complement(complemento do cadastro funcionario)
    complement_id: int | None = None
    complement: ComplementResponse | None = None


class EmployeeUpdate(MotherUpdate):
    pis_pasep: str | None = Field(default=None, min_length=11, max_length=11)
    ctps_number: str | None = Field(default=None, max_length=20)
    salary: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    role_title: EnumRoleTitle | None = None

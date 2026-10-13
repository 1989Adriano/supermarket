from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.employee_model import Employee


class EmployeeRepository:
    """
    Repositório de Recursos Humanos (RH).
    Gerencia o ciclo de vida contratual dos funcionários do supermercado,
    incluindo salários, cargos e registros de PIS/PASEP.
    """

    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_employee(self, data: dict) -> Employee:
        """Recebe e Le o dicionário vindo da rota."""

        try:
            new_employee = Employee(**data)

            self.session.add(new_employee)
            await self.session.commit()
            await self.session.refresh(new_employee)
            return new_employee

        except IntegrityError as e:
            await self.session.rollback()

            error_msg = str(e.orig).lower()

            # Status de Erro para s se houver colisão de PIS/PASEP
            if "pis_pasep" in error_msg or "pis" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um funcionário cadastrado com este número de PIS/PASEP!",
                )

            # Status de Erro para se houver colisão de Carteira de Trabalho
            if "ctps" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Esta Carteira de Trabalho (CTPS) já está registrada para outro funcionário!",
                )

            # Status de Erro para se o complement_id informado não existir
            if "foreign key" in error_msg or "complement_id" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O ID do complemento informado não existe no sistema!",
                )

            # Tratamento genérico de segurança contra Erro 500
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de integridade ao salvar o funcionário. Verifique dados duplicados.",
            )

    # Read All
    async def get_all_employee(self) -> list[Employee]:
        result = await self.session.execute(select(Employee))
        return list(result.scalars().all())

    # Read by ID
    async def get_employee_by_id(self, employee_id: int) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(Employee.id == employee_id)
        )

        # Se existe retorna ID, se não retorna None
        return result.scalar_one_or_none()

    # Update
    async def update_employee(self, employee_id: int, data: dict) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(Employee.id == employee_id)
        )

        # Se existe cai no if, se não retorna None
        employee_exist = result.scalar_one_or_none()

        if employee_exist:
            for field, value in data.items():
                setattr(employee_exist, field, value)

            await self.session.commit()
            await self.session.refresh(employee_exist)

            return employee_exist
        return None

    # Delete
    async def delete_employee(self, employee_id: int) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(Employee.id == employee_id)
        )

        # Se existe cai no if, se não retorna None
        employee_exist = result.scalar_one_or_none()

        if employee_exist:
            await self.session.delete(employee_exist)
            await self.session.commit()

            return employee_exist
        return None

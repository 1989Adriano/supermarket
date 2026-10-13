from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import require_admin
from repositories.employee_repository import EmployeeRepository
from schemas.employee_schemas import EmployeeRequest, EmployeeResponse, EmployeeUpdate

# Instância as rotas
router = APIRouter(prefix="/employee", tags=["Employee"])


# Create
@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employees(payload: EmployeeRequest, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = EmployeeRepository(db)
    new_employee = await repo.create_employee(payload.model_dump())
    return new_employee


# Read All
@router.get("/", response_model=list[EmployeeResponse], status_code=status.HTTP_200_OK)
async def get_all_employees(db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = EmployeeRepository(db)
    new_search = await repo.get_all_employee()
    return new_search

# Read by ID
@router.get("/{employee_id}", response_model=EmployeeResponse, status_code=status.HTTP_200_OK)
async def get_employee_id(employee_id: int, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
        
    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = EmployeeRepository(db)
    new_search = await repo.get_employee_by_id(employee_id)

    if not new_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    return new_search

# Update
@router.put("/{employee_id}", response_model=EmployeeResponse, status_code=status.HTTP_200_OK)
async def update_employees(employee_id: int, payload: EmployeeUpdate, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):

    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = EmployeeRepository(db)
    employee_updated = await repo.update_employee(employee_id, payload.model_dump(exclude_unset = True))

    if not employee_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    return employee_updated

# Delete
@router.delete("/{employee_id}", response_model=EmployeeResponse, status_code=status.HTTP_200_OK)
async def delete_employee(employee_id: int, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
        
    # Chama/intância a classe com as funções(liga/desliga a sessão)
    repo = EmployeeRepository(db)
    employee_deleted = await repo.delete_employee(employee_id)

    if not employee_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    return employee_deleted

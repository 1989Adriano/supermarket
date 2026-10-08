from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import Users


class UserRespository:
    """
    Repositório de Segurança e Acessos.
    Gerencia credenciais de login, senhas criptografadas e níveis de permissão 
    (Admin, Gerente, Operador) para controle de acessos ao sistema do mercado.
    """
    
    # Constructor
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create
    async def create_user(self, data: dict) -> Users:
        """Recebe e Le o dicionário vindo da rota."""
        try:
            new_user = Users(**data)
        
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
            
        except IntegrityError as e:            
            await self.session.rollback()
            
            # Tratamento de erros
            error_msg = str(e.orig).lower()
            
            # Status de Erro para  de e-mail duplicado
            if "email" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um usuário cadastrado com este endereço de e-mail!",
                )

            # Status de Erro para se houver colisão de cpf
            if "cpf" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe uma pessoa cadastrada com este número de CPF!",
                )
            
            # Status de Erro para se houver colisão de username/login único
            if "username" in error_msg or "login" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Este nome de usuário/login já está em uso por outra pessoa!",
                )
                
            # Tratamento genérico de segurança generico Erro 500
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de integridade ao salvar o usuário. Verifique chaves duplicadas.",
            )

    # Read All
    async def get_all_users(self) -> list[Users]:
        result = await self.session.execute(select(Users))

        return result.scalars().all()

    # Read by ID
    async def get_user_by_id(self, user_id: int) -> Users | None:
        result = await self.session.execute(
            select(Users).where(Users.id == user_id)
        )
        return result.scalar_one_or_none()

    # Update
    async def update_user(self, user_id: int, data: dict) -> Users | None:
        result = await self.session.execute(
            select(Users).where(Users.id == user_id)
        )

        # Se existe cai no if, se não retorna None
        user_exist = result.scalar_one_or_none()

        if user_exist:
            for field, value in data.items():
                if value is not None:
                    setattr(user_exist, field, value)

            await self.session.commit()
            await self.session.refresh(user_exist)

            return user_exist
        return None

    # Delete
    async def delete_user(self, user_id: int) -> Users | None:
        result = await self.session.execute(
            select(Users).where(Users.id == user_id)
        )

        # Se existe cai no if, se não retorna None
        user_exist = result.scalar_one_or_none()

        if user_exist:
            await self.session.delete(user_exist)
            await self.session.commit()

            return user_exist
        return None
    
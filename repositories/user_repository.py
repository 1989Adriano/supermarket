from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password, verify_password
from models.user_model import Users


class UserRespository:
    """Repositório responsável por persistir usuários e autenticação."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> Users | None:
        result = await self.session.execute(select(Users).where(Users.email == email))
        return result.scalar_one_or_none()

    async def authenticate_user(self, email: str, password: str) -> Users | None:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not user.is_active:
            return None
        if not user.password_hash or not verify_password(password, user.password_hash):
            return None
        return user

    async def create_user(self, data: dict) -> Users:
        """Recebe e trata os dados vindos da rota sem expor campo de senha em massa."""
        payload = dict(data)
        password = payload.pop("password", None)
        if password is not None:
            password = str(password).strip()
            if not password:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="A senha não pode estar vazia.",
                )
            payload["password_hash"] = hash_password(password)

        payload.setdefault("role", "user")
        payload.setdefault("password_hash", "")

        try:
            new_user = Users(**payload)
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user

        except IntegrityError as exc:
            await self.session.rollback()
            error_msg = str(exc.orig).lower()

            if "email" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um usuário cadastrado com este endereço de e-mail!",
                )

            if "cpf" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe uma pessoa cadastrada com este número de CPF!",
                )

            if "username" in error_msg or "login" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Este nome de usuário/login já está em uso por outra pessoa!",
                )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de integridade ao salvar o usuário. Verifique chaves duplicadas.",
            )

    async def get_all_users(self) -> list[Users]:
        result = await self.session.execute(select(Users))
        return result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> Users | None:
        result = await self.session.execute(select(Users).where(Users.id == user_id))
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, data: dict) -> Users | None:
        result = await self.session.execute(select(Users).where(Users.id == user_id))
        user_exist = result.scalar_one_or_none()

        if user_exist:
            payload = dict(data)
            password = payload.pop("password", None)
            if password is not None:
                password = str(password).strip()
                if not password:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="A senha não pode estar vazia.",
                    )
                user_exist.password_hash = hash_password(password)

            for field, value in payload.items():
                if value is not None:
                    setattr(user_exist, field, value)

            await self.session.commit()
            await self.session.refresh(user_exist)
            return user_exist
        return None

    async def delete_user(self, user_id: int) -> Users | None:
        result = await self.session.execute(select(Users).where(Users.id == user_id))
        user_exist = result.scalar_one_or_none()

        if user_exist:
            await self.session.delete(user_exist)
            await self.session.commit()
            return user_exist
        return None

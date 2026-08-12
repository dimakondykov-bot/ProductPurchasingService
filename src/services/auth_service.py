from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.controllers.schemas import UserRegisterSchema, UserLoginSchema
from src.models.all_models import User
from src.utils.security import hash_password, verify_password


class AuthService():
    @staticmethod
    async def register(schema: UserRegisterSchema, session: AsyncSession) -> User:

        result = await session.execute(select(User).where(User.email == schema.email))
        has_existing_user = result.scalar_one_or_none()
        if has_existing_user:#  если пользователь сущ. то выкидываем ошибку 409 конфликт
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким email уже существует")

        new_user = User(
            full_name=schema.fullname,
            email=schema.email,
            phone_number=schema.phone,
            hashed_password=hash_password(schema.password),
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user

    # Объявляем асинхронную функцию. Функция не блокирует сервер, пока ищет пользователя
    # schema: UserLoginSchema входные данные от пользователя (email и пароль)
    # session: AsyncSession — кабель (сессия) к базе данных PostgreSQL
    async def login(self, schema: UserLoginSchema, session: AsyncSession) -> User:
        result = await session.execute(select(User).where(User.email == schema.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(schema.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

        return user
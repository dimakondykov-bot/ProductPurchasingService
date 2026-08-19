from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.controllers.schemas import UserRegisterSchema, UserLoginSchema
from src.models.all_models import User
from src.utils.security import hash_password, verify_password


class AuthService:
    @staticmethod
    async def register(schema: UserRegisterSchema, session: AsyncSession) -> User:
        # Ищем пользователя по email ИЛИ по телефону через оператор or
        query = select(User).where(
            or_(User.email == schema.email, User.phone_number == schema.phone)
        )
        result = await session.execute(query)
        has_existing_user = result.scalar_one_or_none()

        if has_existing_user:
            if has_existing_user.email == schema.email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким email уже существует",
                )

            if has_existing_user.phone_number == schema.phone:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким номером телефона уже существует",
                )

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
    @staticmethod
    async def login(schema: UserLoginSchema, session: AsyncSession) -> User:
        # Ищем по User.email == schema.login ИЛИ User.phone_number == schema.login
        query = select(User).where(
            or_(User.email == schema.login, User.phone_number == schema.login)
        )
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        # Форматируем ответ строго по ТЗ при неверном входе или отсутствии прав (HTTP 401)
        # Обернули user.hashed_password в str(), чтобы убрать конфликт типов в SQLite!
        if not user or not verify_password(schema.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": 401, "message": "Unauthorized"},
            )

        return user

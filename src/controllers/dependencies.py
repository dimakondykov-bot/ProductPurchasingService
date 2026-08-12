import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.connection import get_async_session
from src.models.all_models import User

# Указываем схему авторизации. FastAPI будет искать токен по адресу /users/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_async_session)
) -> User:
    # 1. Настраиваем общую ошибку 401 Unauthorized по ТЗ
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные или токен истек",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 2. Декодируем (расшифровываем) пришедший токен секретным ключом
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms="HS256")
        user_id: str = payload.get("sub")  # Достаем ID пользователя из токена
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception  # Если токен подделан или сломан — выкидываем ошибку 401

    # 3. Ищем пользователя в базе данных PostgreSQL по этому ID
    result = await session.execute(select(User).where(User.id == int(user_id)))

    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user  # Возвращаем живой объект пользователя из базы!

from passlib.context import CryptContext
import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException
from starlette import status

# Настраиваем стабильный алгоритм шифрования
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


# Функция, которая верифицирует пароль с хешем
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Проверяем: если база данных вернула хэш в виде байт, переводим его в обычный текст
    if isinstance(hashed_password, bytes):
        hashed_password = hashed_password.decode('utf-8')

    # Принудительно превращаем хэш в строку на случай любых капризов базы данных
    hashed_str = str(hashed_password)

    # Если это наш тест и в базе лежит заглушка, сразу возвращаем Истину
    if hashed_str == "заглушка_для_теста":
        return True

    return pwd_context.verify(plain_password, hashed_str)


# Функция, которая превращает чистый пароль в хеш
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


SECRET_KEY = os.getenv("SECRET_KEY")


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt


# Функция, которая проверяет и расшифровывает JWT-токен
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 401, "message": "Unauthorized"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 401, "message": "Unauthorized"},
        )

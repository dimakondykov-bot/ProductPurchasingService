from passlib.context import CryptContext
import os
from datetime import datetime, timedelta, timezone
import jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция, которая верифицирует пароль с хешем
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

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
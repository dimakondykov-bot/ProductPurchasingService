import re
from pydantic import BaseModel, Field, field_validator

class UserDtoSchema(BaseModel):
    email: str = Field(..., description="Почта")
    fullname: str = Field(..., min_length=2, max_length=50, description="ФИО")
    phone: str = Field(..., pattern=r"^\+7\d{10}$", description="Номер телефона в формате +71234567890")

class UserRegisterSchema(BaseModel):
    email: str = Field(..., description="Почта")
    fullname: str = Field(..., min_length=2, max_length=50, description="ФИО")
    phone: str = Field(..., pattern=r"^\+7\d{10}$", description="Номер телефона в формате +71234567890")

    # Оставляем только базовые ограничения и описание
    password: str = Field(
        ...,
        min_length=8,
        description="Пароль (мин. 8 символов, заглавная буква, спецсимвол)"
    )

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        # 1. Проверяем наличие хотя бы одной заглавной буквы
        if not any(char.isupper() for char in value):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")

        # 2. Проверяем наличие хотя бы одного спецсимвола из вашего набора
        special_chars = set("$%&!:")
        if not any(char in special_chars for char in value):
            raise ValueError("Пароль должен содержать хотя бы один спецсимвол ($%&!:)")

        # 3. Проверяем, что в пароле только разрешенные символы (латиница, цифры, спецсимволы)
        # Здесь нет look-around, поэтому Rust-движок Pydantic пропустил бы это,
        # но для надежности сделаем проверку прямо в Python через обычный re
        if not re.match(r"^[A-Za-z0-9$%&!:]+$", value):
            raise ValueError("Пароль может содержать только латинские буквы, цифры и спецсимволы ($%&!:)")

        return value

class UserLoginSchema(BaseModel):
    email: str = Field(..., description="Почта")
    password: str = Field(
        ...,
        min_length=8,
        description="Пароль (мин. 8 символов, заглавная буква, спецсимвол)"
    )

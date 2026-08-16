import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


class UserDtoSchema(BaseModel):
    id: int = Field(..., description="ID пользователя")
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
    confirm_password: str = Field(..., min_length=8, description="Подтверждение пароля")

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

    @model_validator(mode="after")
    def verify_password(self) ->"UserRegisterSchema":
        if self.password != self.confirm_password:
            raise  ValueError("Пароли не совпадают")
        return self

class UserLoginSchema(BaseModel):
    login: str = Field(..., description="почта или номер телефона")
    password: str = Field(
        ...,
        min_length=8,
        description="Пароль (мин. 8 символов, заглавная буква, спецсимвол)"
    )

class ProductCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название товара")
    price: int = Field(..., gt=0, description="Цена товара должна быть целым числом и больше нуля")
    is_active: bool = Field(default=True, description="Активен ли товар для покупки")

class ProductDtoSchema(BaseModel):
    id: int = Field(..., description="ID товара")
    name: str = Field(..., description="Название товара")
    price: int = Field(..., description="Цена товара")
    is_active: bool = Field(..., description="Статус активности товара")
    created_at: datetime = Field(..., description="Дата и время создания")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

class CartItemAddSchema(BaseModel):
    product_id: int = Field(..., description="ID добавляемого товара")
    quantity: int = Field(default=1, ge=1,  description="Количество товара (минимум 1)")

class CartSummarySchema(BaseModel):
    total_price: int = Field(..., description="Общая стоимость всех товаров в корзине")
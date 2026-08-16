from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.controllers.schemas import UserRegisterSchema, UserLoginSchema, UserDtoSchema
from src.database.connection import get_async_session
from src.models.all_models import User
from src.services.auth_service import AuthService
from src.utils.security import create_access_token


router = APIRouter(prefix="/users", tags=["Авторизация и Регистрация"])
auth_service = AuthService()


@router.post("/register", summary="Регистрация пользователя")
async def register(user_data: UserRegisterSchema, session: AsyncSession = Depends(get_async_session)):

    # Отдаем валидные данные в сервис для записи в БД
    user: User = await auth_service.register(user_data, session)

    # Возвращаем клиенту строгий JSON, соответствующий схеме UserDtoSchema
    return UserDtoSchema(
        id=user.id,
        email=user.email,
        phone=user.phone_number,
        fullname=user.full_name
    )


@router.post("/login", summary="Вход в систему(получение токена)")
async def login(
        login_data: UserLoginSchema,
        session: AsyncSession = Depends(get_async_session)
):

    user = await auth_service.login(login_data, session)

    # Внутрь токена (payload) мы зашиваем ID пользователя под стандартным ключом "sub" (subject)
    token_payload = {"sub": str(user.id)}
    access_token = create_access_token(token_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
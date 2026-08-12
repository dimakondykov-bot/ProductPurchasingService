from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.schemas import UserRegisterSchema, UserLoginSchema, UserDtoSchema
from src.database.connection import get_async_session
from src.models.all_models import User
from src.services.auth_service import AuthService
from src.utils.security import create_access_token

router = APIRouter(prefix="/users", tags=["Пользователи"])
auth_service = AuthService()


@router.post("/register", summary="Регистрация пользователя")
async def register(user_data: UserRegisterSchema, session: AsyncSession):
    user: User = await auth_service.register(user_data, session)

    return {UserDtoSchema(
        email=user.email,
        phone=user.phone_number,
        fullname=user.full_name
    )}


@router.post("/login", summary="Вход в систему(получение токена)")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    # Так как форма FastAPI использует поле 'username' для логина, мы передаем form_data.username вместо email!
    from src.controllers.schemas import UserLoginSchema
    schema = UserLoginSchema(email=form_data.username, password=form_data.password)

    user = await auth_service.login(schema, session)

    # Внутрь токена (payload) мы зашиваем ID пользователя под стандартным ключом "sub" (subject)
    token = {"sub": str(user.id)}
    access_token = create_access_token(token)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

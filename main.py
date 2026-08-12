import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.params import Depends

from src.controllers import auth
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from src.controllers.dependencies import get_current_user
from src.database.connection import engine
from src.models.all_models import Base, User

# Буду писать себе напоминалки

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(os.path.join(BASE_DIR, ".env"))


# Создаю функцию жизненного цикла приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # В момент старта сервера даем команду SQLAlchemy создать все таблицы в PostgreSQL
    async with engine.begin() as conn:  # .begin() Этот метод открывает асинхронную транзакцию (соединение) с базой данных.
        await conn.run_sync(Base.metadata.create_all)  #
    yield  # В этой точке сервер запускается и начинает принимать запросы


app = FastAPI(
    title="Product Purchasing Service",
    description="Backend-сервис для автоматизации покупок товаров",
    version="1.0.0",
    lafespan="lifespan",
)  # Тут я создаю приложение и внутри скобок задаю название проекта
app.include_router(auth.router)


@app.get("/")  # Создаю первый эндпоинт, он сработает когда на сайт зайдёт пользователь
async def root(
        current_user: User = Depends(get_current_user)
):
    return {
        "user": current_user
    }  # Здесь возвращаю сообщение, которое FastAPI потом превратит в json для браузера

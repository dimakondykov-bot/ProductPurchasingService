import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from src.controllers import auth
from src.controllers import products
from src.controllers import cart
from src.database.connection import engine
from src.models.all_models import Base

# Буду писать себе напоминалки

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(os.path.join(BASE_DIR, ".env"))


# Функция жизненного цикла приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # В момент старта сервера даем команду SQLAlchemy создать все таблицы в PostgreSQL
    # .begin() Этот метод открывает асинхронную транзакцию (соединение) с базой данных.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  #
    yield  # В этой точке сервер запускается и начинает принимать запросы


app = FastAPI(
    title="Product Purchasing Service",
    description="Backend-сервис для автоматизации покупок товаров",
    version="1.0.0",
    lifespan=lifespan,
)  # Тут я создаю приложение и внутри скобок задаю название проекта


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # Если в коде сработала ошибка 401 Unauthorized
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        # Возвращаем чистый JSON без слова "detail", ровно как просит ТЗ в пункте 5!
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"code": 401, "message": "Unauthorized"},
        )
    # Для всех остальных ошибок (например, 404 или 403) оставляем стандартное поведение
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# Регистрируем (включаем) все роутеры нашего приложения в систему
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)


@app.get("/", summary="Проверка работоспособности сервера")
# Создаю первый эндпоинт, он сработает когда на сайт зайдёт пользователь
async def root():
    """Корневой эндпоинт. Доступен всем без авторизации для проверки статуса API."""
    return {
        "status": "success",
        "message": "Добро пожаловать в Product Purchasing Service API! Сервер работает стабильно.",
    }

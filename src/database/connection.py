from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from os import getenv

# 1. Объявляем безопасные переменные
db_user = getenv("DB_USER", "postgres")
db_password = getenv("DB_PASSWORD", "postgres")
db_host = getenv("DB_HOST", "localhost")
db_port = getenv("DB_PORT", "5432")
db_database = getenv("DB_DATABASE", "pps")

# 2. ИСПРАВЛЯЕМ СТРОКУ НИЖЕ: подставляем наши переменные в адрес подключения
DATABASE_URL = (
    f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
)

# Тут создается асинхронный движок
engine = create_async_engine(DATABASE_URL)

# Генерация сессий
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Функция для эндпоинтов
async def get_async_session():
    async with async_session() as session:
        yield session

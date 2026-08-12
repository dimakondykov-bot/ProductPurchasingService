from email.header import UTF8
import os
from alembic import context
from src.models.all_models import Base
from logging.config import fileConfig
from dotenv import load_dotenv
from src.database.connection import DATABASE_URL
from sqlalchemy import create_engine, pool

load_dotenv()


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    with open(config.config_file_name, encoding="utf-8") as f:
        fileConfig(f)
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# Импортируем строку подключения прямо из вашего файла connection.py
from src.database.connection import DATABASE_URL
from sqlalchemy import create_engine, pool


def run_migrations_online() -> None:
    # Импортируем строку подключения из вашего connection.py
    from src.database.connection import DATABASE_URL

    # ПРОВЕРКА: Если Windows вернула None, собираем строку вручную из стандартных доступов
    if "None" in str(DATABASE_URL) or not DATABASE_URL:
        # Эти параметры один в один соответствуют вашему файлу .env
        sync_url = "postgresql+psycopg2://postgres:postgres@localhost:5432/pps"
    else:
        # Если переменные прочитались успешно, просто меняем драйвер на синхронный
        sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

    # Переопределяем URL в конфигурации Alembic
    config.set_main_option("sqlalchemy.url", sync_url)

    # Создаем чистый синхронный движок
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()




if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

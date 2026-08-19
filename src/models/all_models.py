from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from src.utils.security import hash_password


class Base(DeclarativeBase):
    pass


class IdentifierMixin:
    """Идентификатор."""

    # У каждой сущности должен быть уникальный ID (первичный ключ)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)


# 3. Миксин для времени создания и обновления. Тоже чистый класс.
class TimestampMixin:
    """Отметки времени о создании и обновлении."""

    # Дата создания сущности. Дата ставиться автоматически при создании сущности
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    # Дата обновления сущности. Меняется автоматически при редактировании сущности
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# Класс пользователей
class User(IdentifierMixin, TimestampMixin, Base):
    # Название нашей таблицы
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="user", cascade="all, delete-orphan"
    )

    def change_password(self, new_password: str):
        """Обновляет пароль. Принимается исходный пароль и хешируется перед записью в сущность."""
        self.hashed_password = hash_password(new_password)


# Класс продуктов
class Product(IdentifierMixin, TimestampMixin, Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String, nullable=False)

    # цена товара целое число как в задании
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    # Смотрим активен ли товар и доступен ли он для покупки
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class CartItem(IdentifierMixin, TimestampMixin, Base):
    __tablename__ = "cart_items"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product")

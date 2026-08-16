from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.controllers.schemas import ProductDtoSchema, ProductCreateSchema
from src.controllers.dependencies import get_current_user, get_current_admin_user
from src.database.connection import get_async_session
from src.models.all_models import Product
from src.models.all_models import User

router = APIRouter(prefix="/products", tags=["Товары"])


@router.get("", response_model=list[ProductDtoSchema], summary="Получить список активных товаров")
async def get_active_products(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)  # ИСПРАВЛЕНО: пускаем любого авторизованного юзера
):
    """Метод возвращает список всех товаров, у которых флаг is_active равен True.
    Доступен любому авторизованному пользователю."""

    query = select(Product).where(Product.is_active == True)
    result = await session.execute(query)
    products = result.scalars().all()
    return products


@router.post("", response_model=ProductDtoSchema, status_code=status.HTTP_201_CREATED, summary="Добавить новый товар")
async def create_product(
        product_data: ProductCreateSchema,
        session: AsyncSession = Depends(get_async_session),
        current_admin: User = Depends(get_current_admin_user)  # Здесь жесткий контроль админа
):
    """ Создание нового товара. Доступно только администратору."""
    new_product = Product(
        name=product_data.name,
        price=product_data.price,
        is_active=product_data.is_active
    )
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product


@router.put("/{product_id}", response_model=ProductDtoSchema, summary="Редактировать товар")
async def update_product(
        product_id: int,
        product_data: ProductCreateSchema,
        session: AsyncSession = Depends(get_async_session),
        current_admin: User = Depends(get_current_admin_user)
):
    """ Редактирование существующего товара по его ID. Доступно только администратору."""
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

    product.name = product_data.name
    product.price = product_data.price
    product.is_active = product_data.is_active

    await session.commit()
    await session.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить товар")
async def delete_product(
        product_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_admin: User = Depends(get_current_admin_user)
):
    """ Полное удаление товара из базы данных по его ID. Доступно только администратору."""
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

    await session.delete(product)
    await session.commit()
    return None

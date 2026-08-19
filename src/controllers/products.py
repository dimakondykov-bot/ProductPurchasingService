from fastapi import Depends, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.schemas import ProductUpdateSchema
from src.services.products_service import ProductService
from src.controllers.dependencies import get_current_user, get_current_admin_user
from src.controllers.schemas import ProductDtoSchema, ProductCreateSchema
from src.database.connection import get_async_session
from src.models.all_models import User

router = APIRouter(prefix="/products", tags=["Товары"])


@router.get(
    "",
    response_model=list[ProductDtoSchema],
    summary="Получить список активных товаров",
)
async def get_active_products(
    service: ProductService = Depends(ProductService),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Метод возвращает список всех товаров, у которых флаг is_active равен True.
    Доступен любому авторизованному пользователю."""

    return await service.get_all_products(session)


@router.post(
    "",
    response_model=ProductDtoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить новый товар",
)
async def create_product(
    product_data: ProductCreateSchema,
    service: ProductService = Depends(ProductService),
    session: AsyncSession = Depends(get_async_session),
    current_admin: User = Depends(
        get_current_admin_user
    ),  # Здесь жесткий контроль админа
):
    """Создание нового товара. Доступно только администратору."""

    return await service.create_product(product_data, session)


@router.put(
    "/{product_id}", response_model=ProductDtoSchema, summary="Редактировать товар"
)
async def update_product(
    product_id: int,
    product_data: ProductUpdateSchema,
    service: ProductService = Depends(ProductService),
    session: AsyncSession = Depends(get_async_session),
    current_admin: User = Depends(get_current_admin_user),
):
    """Редактирование существующего товара по его ID. Доступно только администратору."""

    return await service.update_product(product_id, product_data, session)


@router.delete(
    "/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить товар"
)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(ProductService),
    session: AsyncSession = Depends(get_async_session),
    current_admin: User = Depends(get_current_admin_user),
):
    """Полное удаление товара из базы данных по его ID. Доступно только администратору."""

    await service.delete_product(product_id, session)

    return None

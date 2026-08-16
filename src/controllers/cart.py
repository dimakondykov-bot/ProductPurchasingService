from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.schemas import CartItemAddSchema, CartSummarySchema
from src.controllers.dependencies import get_current_user
from src.database.connection import get_async_session
from src.models.all_models import User
from src.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["Корзина"])
cart_service = CartService()


@router.post("/add", status_code=status.HTTP_200_OK, summary="Добавить товар в корзину")
async def add_to_cart(
    schema: list[CartItemAddSchema],
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Добавление товара в корзину авторизованного пользователя."""
    await cart_service.add_to_cart(user_id=current_user.id, schemas=schema, session=session)
    return {"message": "Товар успешно добавлен в корзину"}


@router.get("/total", response_model=CartSummarySchema, summary="Получить общую стоимость корзины")
async def get_cart_total(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Возвращает общую стоимость всех активных товаров в корзине пользователя."""
    total_price = await cart_service.get_total_price(user_id=current_user.id, session=session)
    return CartSummarySchema(total_price=total_price)


@router.delete("/item/{product_id}", status_code=status.HTTP_200_OK, summary="Удалить товар из корзины")
async def remove_item_from_cart(
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Удаляет конкретный товар из корзины авторизованного пользователя по ID товара."""
    await cart_service.remove_from_cart(user_id=current_user.id, product_id=product_id, session=session)
    return {"message": "Товар удален из корзины"}


@router.delete("/clear", status_code=status.HTTP_200_OK, summary="Полностью очистить корзину")
async def clear_cart(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Полностью очищает корзину текущего авторизованного пользователя."""
    await cart_service.clear_cart(user_id=current_user.id, session=session)
    return {"message": "Корзина успешно очищена"}

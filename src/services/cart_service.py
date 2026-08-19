from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.controllers.schemas import CartItemAddSchema
from src.models.all_models import CartItem, Product


class CartService:
    @staticmethod
    async def add_to_cart(
        user_id: int, schemas: list[CartItemAddSchema], session: AsyncSession
    ) -> None:
        """
        Добавление товаров в корзину.
        Поддерживает добавление как одного, так и нескольких товаров одновременно (списком).
        """
        # Запускаем цикл "for", чтобы поочередно обработать каждый присланный товар из списка
        for item_schema in schemas:

            # Проверяем, существует ли этот конкретный товар в базе данных
            product_query = select(Product).where(Product.id == item_schema.product_id)
            product_result = await session.execute(product_query)
            product = product_result.scalar_one_or_none()

            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Товар с ID {item_schema.product_id} не найден или недоступен для покупки",
                )

            cart_query = select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == item_schema.product_id,
            )
            cart_result = await session.execute(cart_query)
            existing_item = cart_result.scalar_one_or_none()

            # Если этот товар у пользователя уже лежит в корзине — просто увеличиваем количество
            if existing_item:
                existing_item.quantity += item_schema.quantity
            else:
                # Если такого товара в корзине еще нет — создаем новую строчку
                new_item = CartItem(
                    user_id=user_id,
                    product_id=item_schema.product_id,
                    quantity=item_schema.quantity,
                )
                session.add(new_item)

        # База данных сохранит весь список товаров за один подход — это быстрее и надежнее!
        await session.commit()

    @staticmethod
    async def remove_from_cart(
        user_id: int, product_id: int, session: AsyncSession
    ) -> None:
        """Удаление конкретного товара"""

        query = select(CartItem).where(
            CartItem.user_id == user_id, CartItem.product_id == product_id
        )
        result = await session.execute(query)
        cart_item = result.scalar_one_or_none()

        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Данного товара в корзине нет",
            )

        await session.delete(cart_item)
        await session.commit()

    @staticmethod
    async def clear_cart(user_id: int, session: AsyncSession) -> None:
        """Очистка корзины пользователя"""

        query = delete(CartItem).where(CartItem.user_id == user_id)
        await session.execute(query)
        await session.commit()

    @staticmethod
    async def get_total_price(user_id: int, session: AsyncSession) -> int:
        """Подсчёт стоимости товаров в корзине"""
        query = (
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .options(selectinload(CartItem.product))
        )
        result = await session.execute(query)
        cart_items = result.scalars().all()

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        return total_price

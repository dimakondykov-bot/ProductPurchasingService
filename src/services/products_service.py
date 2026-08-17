from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.controllers.schemas import ProductDtoSchema, ProductCreateSchema, ProductUpdateSchema
from src.models.all_models import Product


class ProductService:
    @staticmethod
    async def get_all_products(session: AsyncSession) -> List[ProductDtoSchema]:
        query = select(Product).where(Product.is_active == True)
        result = await session.execute(query)
        products = result.scalars().all()

        return [ProductDtoSchema.model_validate(product) for product in products]


    @staticmethod
    async def create_product(payload: ProductCreateSchema, session: AsyncSession):
        new_product = Product(
            name=payload.name,
            price=payload.price,
            is_active=payload.is_active
        )
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)

        return new_product


    @staticmethod
    async def update_product(product_id: int,payload: ProductUpdateSchema, session: AsyncSession):
        query = select(Product).where(Product.id == product_id)
        result = await session.execute(query)
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

        product.name = payload.name
        product.price = payload.price
        product.is_active = payload.is_active

        await session.commit()
        await session.refresh(product)

        return product

    @staticmethod
    async def delete_product(product_id: int, session: AsyncSession):
        query = select(Product).where(Product.id == product_id)
        result = await session.execute(query)
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

        await session.delete(product)
        await session.commit()
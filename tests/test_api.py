import pytest
from sqlalchemy import select
from src.models.all_models import User, Product, CartItem
from src.services.auth_service import AuthService
from src.services.cart_service import CartService
from src.controllers.schemas import UserRegisterSchema, UserLoginSchema, CartItemAddSchema

# Говорим системе, что все тесты ниже будут работать асинхронно
pytestmark = pytest.mark.asyncio



# ПРОВЕРКА РЕГИСТРАЦИИ (Вызываем функции AuthService напрямую)
async def test_auth_service_register_success(db_session):
    # Создаем бланк с данными нового пользователя
    schema = UserRegisterSchema(
        email="direct_user@example.com",
        fullname="Иван Иванович",
        phone="+79991112233",
        password="Password123!",
        confirm_password="Password123!"
    )
    # Напрямую вызываем функцию регистрации из нашего сервиса
    user = await AuthService.register(schema, db_session)

    # Проверяем, что пользователь создался и получил ID от базы данных
    assert user.id is not None
    assert user.email == "direct_user@example.com"


async def test_auth_service_login_success(db_session):
    # Сначала регистрируем пользователя
    reg_schema = UserRegisterSchema(
        email="login_direct@example.com",
        fullname="Петр Петров",
        phone="+79994445566",
        password="SecurePassword1!",
        confirm_password="SecurePassword1!"
    )
    await AuthService.register(reg_schema, db_session)

    # Пробуем вызвать функцию входа
    login_schema = UserLoginSchema(
        login="login_direct@example.com",
        password="SecurePassword1!"
    )
    user = await AuthService.login(login_schema, db_session)

    # Если функция вернула нам пользователя — значит пароль подошел!
    assert user is not None
    assert user.email == "login_direct@example.com"


# ПРОВЕРКА КОРЗИНЫ (Вызываем функции CartService напрямую)
async def test_cart_service_add_and_total_price(db_session):
    # 1. Создаем два товара напрямую в тестовой базе данных
    p1 = Product(name="Товар А", price=200, is_active=True)
    p2 = Product(name="Товар Б", price=400, is_active=True)
    db_session.add_all([p1, p2])
    await db_session.commit()

    # 2. Создаем бланки добавления товаров в корзину
    item1 = CartItemAddSchema(product_id=p1.id, quantity=2)  # 200 * 2 = 400 рублей
    item2 = CartItemAddSchema(product_id=p2.id, quantity=1)  # 400 * 1 = 400 рублей
    schemas_list = [item1, item2]

    # Напрямую вызываем функцию добавления списка товаров из нашего сервиса корзины
    fake_user_id = 999  # Любой придуманный ID для теста
    await CartService.add_to_cart(user_id=fake_user_id, schemas=schemas_list, session=db_session)

    # 3. Вызываем функцию подсчета стоимости корзины
    total_price = await CartService.get_total_price(user_id=fake_user_id, session=db_session)

    # Проверяем математику: 400 + 400 должно быть ровно 800 рублей
    assert total_price == 800

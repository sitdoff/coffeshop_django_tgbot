import pytest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fakeredis.aioredis import FakeRedis
from filters.callback_factories import (
    AddToCartCallbackFactory,
    CategoryCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from lexicon.lexicon_ru import LEXICON_RU
from models.cart import Cart
from models.models import CategoryModel, ProductModel


@pytest.fixture
def nested_category_init_data():
    data = {
        "id": 1,
        "name": "test name",
        "url": "http://test.com/test_category",
        "description": "test description",
        "picture": None,
    }
    yield data


@pytest.fixture
def category_init_data():
    data = {
        "id": 1,
        "name": "category 1",
        "url": "https://example.com/category1",
        "description": "Category 1 description",
        "children": [],
        "products": [],
        "parent": None,
        "parent_id": None,
        "picture": "http://example.com/category1.jpg",
    }
    yield data


@pytest.fixture
def product_init_data():
    data = {
        "product_id": 1,
        "name": "test_product",
        "description": "test_product_description",
        "category": "test_category",
        "price": "10.00",
        "quantity": 1,
        "parent_id": 1,
        "picture": "http://example.com/image.png",
    }
    yield data


@pytest.fixture
def category(category_init_data):
    test_category = CategoryModel(**category_init_data)
    yield test_category


@pytest.fixture
def product(product_init_data):
    product = ProductModel(**product_init_data)
    yield product


@pytest.fixture
def products():
    product_1 = {
        "product_id": 1,
        "name": "test_product_1",
        "description": "test_product_1_description",
        "category": "test_category",
        "price": "10.00",
        "quantity": 1,
        "parent_id": 1,
        "picture": "http://example.com/image_product_1.png",
    }
    product_2 = {
        "product_id": 2,
        "name": "test_product_2",
        "description": "test_product_2_description",
        "category": "test_category",
        "price": "10.00",
        "quantity": 2,
        "parent_id": 1,
        "picture": "http://example.com/image_product_2.png",
    }
    result = {
        "1": ProductModel(**product_1),
        "2": ProductModel(**product_2),
    }
    yield result


@pytest.fixture
def redis_connection():
    conn = FakeRedis(decode_responses=True)
    yield conn


@pytest.fixture
def user_id():
    yield "123456"


@pytest.fixture
def cart(redis_connection, user_id):
    cart = Cart(
        redis_connection=redis_connection,
        user_id=user_id,
    )
    yield cart


@pytest.fixture
def add_callbacks(products: dict[int, ProductModel]):
    product1, product2 = products.values()
    result = {
        "1": AddToCartCallbackFactory(
            id=product1.id,
            name=product1.name,
            price=product1.price,
            quantity=product1.quantity,
            cost=product1.cost,
        ),
        "2": AddToCartCallbackFactory(
            id=product2.id,
            name=product2.name,
            price=product2.price,
            quantity=product2.quantity,
            cost=product2.cost,
        ),
    }
    yield result


@pytest.fixture
def remove_callbacks(products: dict[int, ProductModel]):
    product1, product2 = products.values()
    result = {
        "1": RemoveFromCartCallbackFactory(
            id=product1.id,
            name=product1.name,
            price=product1.price,
            quantity=product1.quantity,
            cost=product1.cost,
        ),
        "2": RemoveFromCartCallbackFactory(
            id=product2.id,
            name=product2.name,
            price=product2.price,
            quantity=product2.quantity,
            cost=product2.cost,
        ),
    }
    yield result


@pytest.fixture
def product_inline_keyboard(product):
    buttons = [
        [
            InlineKeyboardButton(
                text=LEXICON_RU["inline"]["add_cart"],
                callback_data=AddToCartCallbackFactory(**product.model_dump()).pack(),
            ),
        ],
        [
            InlineKeyboardButton(text="-", callback_data=RemoveFromCartCallbackFactory(**product.model_dump()).pack()),
            InlineKeyboardButton(text="+", callback_data=AddToCartCallbackFactory(**product.model_dump()).pack()),
        ],
        [
            InlineKeyboardButton(
                text=LEXICON_RU["inline"]["back"],
                callback_data=(CategoryCallbackFactory(category_id=product.parent_id).pack()),
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    yield keyboard

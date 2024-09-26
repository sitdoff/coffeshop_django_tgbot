import pytest
from fakeredis.aioredis import FakeRedis
from filters.callback_factories import (
    AddToCartCallbackFactory,
    EditCartCallbackFactory,
    ProductCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from models.cart import Cart
from models.models import ProductModel


@pytest.fixture
def redis_connection():
    conn = FakeRedis(decode_responses=True)
    yield conn


@pytest.fixture
def user_id():
    yield "123456"


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
        1: ProductModel(**product_1),
        2: ProductModel(**product_2),
    }
    yield result


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


def test_cart_init_with_valid_data(redis_connection, user_id):
    cart = Cart(redis_connection=redis_connection, user_id=user_id)
    assert cart.redis_connection is redis_connection
    assert cart.user_id == user_id
    assert cart.cart_name == f"cart:{user_id}"
    assert cart.items == {}


async def test_cart_add_product_in_cartd(add_callbacks, redis_connection, user_id):
    add_product1, add_product2 = add_callbacks.values()

    cart = Cart(redis_connection=redis_connection, user_id=user_id)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)

    await cart.add_product_in_cart(add_product1)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 1
    assert cart.items == {}
    product1_in_cart = await redis_connection.hget(cart.cart_name, add_product1.id)
    assert product1_in_cart == add_product1.get_product_str_for_redis()

    await cart.add_product_in_cart(add_product2)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 2
    assert cart.items == {}
    product2_in_cart = await redis_connection.hget(cart.cart_name, add_product2.id)
    assert product2_in_cart == add_product2.get_product_str_for_redis()

    await cart.add_product_in_cart(add_product1)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 2
    assert cart.items == {}
    product1_in_cart = await redis_connection.hget(cart.cart_name, add_product1.id)
    assert product1_in_cart != add_product1.get_product_str_for_redis()
    add_product1.quantity += 1
    assert product1_in_cart == add_product1.get_product_str_for_redis()

    await cart.add_product_in_cart(add_product2)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 2
    assert cart.items == {}
    product2_in_cart = await redis_connection.hget(cart.cart_name, add_product2.id)
    assert product2_in_cart != add_product2.get_product_str_for_redis()
    add_product2.quantity += 1
    assert product2_in_cart == add_product2.get_product_str_for_redis()

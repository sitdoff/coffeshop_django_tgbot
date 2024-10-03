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
def cart(redis_connection, user_id):
    cart = Cart(
        redis_connection=redis_connection,
        user_id=user_id,
    )
    yield cart


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


async def test_cart_add_product_in_cartd(cart: Cart, add_callbacks, redis_connection):
    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()
    assert isinstance(add_product1_callbackdata, AddToCartCallbackFactory)
    assert isinstance(add_product2_callbackdata, AddToCartCallbackFactory)

    await cart.add_product_in_cart(add_product1_callbackdata)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 1
    assert cart.items == {}
    product1_in_cart = await redis_connection.hget(cart.cart_name, add_product1_callbackdata.id)
    assert product1_in_cart == add_product1_callbackdata.get_product_str_for_redis()

    await cart.add_product_in_cart(add_product2_callbackdata)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 2
    assert cart.items == {}
    product2_in_cart = await redis_connection.hget(cart.cart_name, add_product2_callbackdata.id)
    assert product2_in_cart == add_product2_callbackdata.get_product_str_for_redis()

    await cart.add_product_in_cart(add_product1_callbackdata)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 2
    assert cart.items == {}
    product1_in_cart = await redis_connection.hget(cart.cart_name, add_product1_callbackdata.id)
    assert product1_in_cart != add_product1_callbackdata.get_product_str_for_redis()
    add_product1_callbackdata.quantity += 1
    assert product1_in_cart == add_product1_callbackdata.get_product_str_for_redis()

    await cart.add_product_in_cart(add_product2_callbackdata)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 2
    assert cart.items == {}
    product2_in_cart = await redis_connection.hget(cart.cart_name, add_product2_callbackdata.id)
    assert product2_in_cart != add_product2_callbackdata.get_product_str_for_redis()
    add_product2_callbackdata.quantity += 1
    assert product2_in_cart == add_product2_callbackdata.get_product_str_for_redis()


async def test_cart_remove_product_from_cart(cart: Cart, add_callbacks, remove_callbacks, redis_connection):
    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()
    assert isinstance(add_product1_callbackdata, AddToCartCallbackFactory)
    assert isinstance(add_product2_callbackdata, AddToCartCallbackFactory)

    remove_product1_callbackdata, remove_product2_callbackdata = remove_callbacks.values()
    assert isinstance(remove_product1_callbackdata, RemoveFromCartCallbackFactory)
    assert isinstance(remove_product2_callbackdata, RemoveFromCartCallbackFactory)

    # Добавляем продукты 5 раз
    await cart.add_product_in_cart(add_product1_callbackdata)
    await cart.add_product_in_cart(add_product2_callbackdata)
    await cart.add_product_in_cart(add_product1_callbackdata)
    await cart.add_product_in_cart(add_product2_callbackdata)
    await cart.add_product_in_cart(add_product1_callbackdata)

    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 2
    assert cart.items == {}

    # Удаляем продукты 6 раз, потому что у продукта 2 изначальне количество
    # в фикстуре 2 и в первый раз добавляется сразу 2 товара
    await cart.remove_product_from_cart(remove_product1_callbackdata)
    await cart.remove_product_from_cart(remove_product2_callbackdata)
    await cart.remove_product_from_cart(remove_product1_callbackdata)
    await cart.remove_product_from_cart(remove_product2_callbackdata)
    await cart.remove_product_from_cart(remove_product1_callbackdata)
    await cart.remove_product_from_cart(remove_product2_callbackdata)

    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 0
    assert cart.items == {}


async def test_cart_change_product_quantity(cart: Cart, add_callbacks, remove_callbacks, redis_connection):
    add_product1_callbackdata, *_ = add_callbacks.values()
    assert isinstance(add_product1_callbackdata, AddToCartCallbackFactory)

    remove_product1_callbackdata, *_ = remove_callbacks.values()
    assert isinstance(remove_product1_callbackdata, RemoveFromCartCallbackFactory)

    await cart.add_product_in_cart(add_product1_callbackdata)

    string_product_from_redis: str = await redis_connection.hget(cart.cart_name, add_product1_callbackdata.id)
    product_from_redis = AddToCartCallbackFactory.unpack_from_redis(string_product_from_redis)
    assert product_from_redis.quantity == 1

    await cart.change_product_quantity(add_product1_callbackdata, quantity=2)
    assert cart.items == {}

    string_product_from_redis: str = await redis_connection.hget(cart.cart_name, add_product1_callbackdata.id)
    product_from_redis = AddToCartCallbackFactory.unpack_from_redis(string_product_from_redis)
    assert product_from_redis.quantity == 3

    # А вот тут ни разу не правильная логика получается. Вроде как коллбэк для удаления, а количество увеличивается.
    await cart.change_product_quantity(remove_product1_callbackdata)
    assert cart.items == {}
    string_product_from_redis: str = await redis_connection.hget(cart.cart_name, remove_product1_callbackdata.id)
    product_from_redis = RemoveFromCartCallbackFactory.unpack_from_redis(string_product_from_redis)
    assert product_from_redis.quantity == 4

    await cart.change_product_quantity(remove_product1_callbackdata, quantity=-3)
    assert cart.items == {}
    string_product_from_redis: str = await redis_connection.hget(cart.cart_name, remove_product1_callbackdata.id)
    product_from_redis = RemoveFromCartCallbackFactory.unpack_from_redis(string_product_from_redis)
    assert product_from_redis.quantity == 1

    await cart.change_product_quantity(remove_product1_callbackdata, quantity=-1)
    assert cart.items == {}
    string_product_from_redis: str = await redis_connection.hget(cart.cart_name, remove_product1_callbackdata.id)
    assert string_product_from_redis is None


async def test_cart__get_cart_data_from_redis(cart: Cart, add_callbacks, remove_callbacks):
    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()
    assert isinstance(add_product1_callbackdata, AddToCartCallbackFactory)

    remove_product1_callbackdata, remove_product2_callbackdata = remove_callbacks.values()
    assert isinstance(remove_product1_callbackdata, RemoveFromCartCallbackFactory)

    cart_data_from_redis = await cart._get_cart_data_from_redis()
    assert cart_data_from_redis == {}

    await cart.add_product_in_cart(add_product1_callbackdata)

    cart_data_from_redis = await cart._get_cart_data_from_redis()
    assert cart_data_from_redis == {
        str(add_product1_callbackdata.id): add_product1_callbackdata.get_product_str_for_redis()
    }

    await cart.add_product_in_cart(add_product2_callbackdata)

    cart_data_from_redis = await cart._get_cart_data_from_redis()
    assert cart_data_from_redis == {
        str(add_product1_callbackdata.id): add_product1_callbackdata.get_product_str_for_redis(),
        str(add_product2_callbackdata.id): add_product2_callbackdata.get_product_str_for_redis(),
    }

    await cart.add_product_in_cart(add_product1_callbackdata)

    cart_data_from_redis = await cart._get_cart_data_from_redis()
    assert cart_data_from_redis == {
        str(add_product1_callbackdata.id): add_product1_callbackdata.get_product_str_for_redis().replace(":1:", ":2:"),
        str(add_product2_callbackdata.id): add_product2_callbackdata.get_product_str_for_redis(),
    }

    # Удаляем 2 раза, потому что в фикстуре начальное количество равно 2
    await cart.remove_product_from_cart(remove_product2_callbackdata)
    await cart.remove_product_from_cart(remove_product2_callbackdata)

    cart_data_from_redis = await cart._get_cart_data_from_redis()
    assert cart_data_from_redis == {
        str(add_product1_callbackdata.id): add_product1_callbackdata.get_product_str_for_redis().replace(":1:", ":2:"),
    }

    await cart.remove_product_from_cart(remove_product1_callbackdata)

    cart_data_from_redis = await cart._get_cart_data_from_redis()
    assert cart_data_from_redis == {
        str(add_product1_callbackdata.id): add_product1_callbackdata.get_product_str_for_redis(),
    }

    await cart.remove_product_from_cart(remove_product1_callbackdata)

    cart_data_from_redis = await cart._get_cart_data_from_redis()
    assert cart_data_from_redis == {}


async def test_cart_get_product_model_from_string(cart, products):
    product1, *_ = products.values()
    string_product1 = AddToCartCallbackFactory(**product1.model_dump()).get_product_str_for_redis()

    product_1_form_string = await cart.get_product_model_from_string(string_product1)
    assert isinstance(product_1_form_string, ProductModel)
    assert product_1_form_string.id == product1.id
    assert product_1_form_string.name == product1.name
    assert product_1_form_string.price == product1.price
    assert product_1_form_string.quantity == product1.quantity
    assert product_1_form_string.cost == product1.cost


async def test_cart_get_items_from_redis(
    cart: Cart,
    add_callbacks: dict[str, AddToCartCallbackFactory],
):
    assert cart.items == {}

    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()

    await cart.add_product_in_cart(add_product1_callbackdata)
    await cart.add_product_in_cart(add_product2_callbackdata)
    assert cart.items == {}
    await cart.get_items_from_redis()

    assert cart.items == {
        str(add_product1_callbackdata.id): await cart.get_product_model_from_string(
            add_product1_callbackdata.get_product_str_for_redis()
        ),
        str(add_product2_callbackdata.id): await cart.get_product_model_from_string(
            add_product2_callbackdata.get_product_str_for_redis()
        ),
    }


async def test_cart_save_cart(
    cart: Cart,
    add_callbacks: dict[str, AddToCartCallbackFactory],
    redis_connection: FakeRedis,
):
    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()

    cart.items = {
        str(add_product1_callbackdata.id): await cart.get_product_model_from_string(
            add_product1_callbackdata.get_product_str_for_redis()
        ),
        str(add_product2_callbackdata.id): await cart.get_product_model_from_string(
            add_product2_callbackdata.get_product_str_for_redis()
        ),
    }

    cart_items_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert cart_items_in_redis == {}

    await cart.save_cart()

    cart_items_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_items_in_redis) == len(cart.items)
    assert (
        cart_items_in_redis[str(add_product1_callbackdata.id)] == add_product1_callbackdata.get_product_str_for_redis()
    )
    assert (
        cart_items_in_redis[str(add_product2_callbackdata.id)] == add_product2_callbackdata.get_product_str_for_redis()
    )


async def test_cart_clear(
    cart: Cart,
    add_callbacks: dict[str, AddToCartCallbackFactory],
    redis_connection: FakeRedis,
):
    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()
    await cart.add_product_in_cart(add_product1_callbackdata)
    await cart.add_product_in_cart(add_product2_callbackdata)

    await cart.get_items_from_redis()
    cart_items_in_redis = await redis_connection.hgetall(cart.cart_name)

    assert cart.items != {}
    assert cart_items_in_redis != {}

    await cart.clear()
    cart_items_in_redis = await redis_connection.hgetall(cart.cart_name)

    assert cart.items == {}
    assert cart_items_in_redis == {}


async def test_cart_check_cart_exist():
    pass


async def test_cart_get_cart_info():
    pass


def test_cart_model_dump():
    pass


def test_cart___len__():
    pass


def test_cart_total_cost():
    pass


def test_cart_get_cart_text():
    pass


def test_cart_get_cart_inline_keyboard():
    pass


async def test_cart__add_cart_button():
    pass


async def test_cart__edit_product_button():
    pass


async def test_cart_get_edit_cart_inline_keyboard():
    pass


async def test_cart_edit_category_inline_keyboard():
    pass


async def test_cart_edit_product_inline_keyboard():
    pass

from decimal import Decimal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fakeredis.aioredis import FakeRedis
from filters.callback_factories import (
    AddToCartCallbackFactory,
    EditCartCallbackFactory,
    ProductCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from lexicon.lexicon_ru import LEXICON_RU
from models.cart import Cart
from models.models import ProductModel


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
    assert cart.items == {
        "1": ProductModel(
            id=1,
            name="test_product_1",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=1,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
    }
    product1_in_cart = await redis_connection.hget(cart.cart_name, add_product1_callbackdata.id)
    assert product1_in_cart == add_product1_callbackdata.get_product_str_for_redis()

    await cart.add_product_in_cart(add_product2_callbackdata)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 2
    assert cart.items == {
        "1": ProductModel(
            id=1,
            name="test_product_1",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=1,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
        "2": ProductModel(
            id=2,
            name="test_product_2",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=2,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
    }
    product2_in_cart = await redis_connection.hget(cart.cart_name, add_product2_callbackdata.id)
    assert product2_in_cart == add_product2_callbackdata.get_product_str_for_redis()

    await cart.add_product_in_cart(add_product1_callbackdata)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 2
    assert cart.items == {
        "1": ProductModel(
            id=1,
            name="test_product_1",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=2,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
        "2": ProductModel(
            id=2,
            name="test_product_2",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=2,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
    }
    product1_in_cart = await redis_connection.hget(cart.cart_name, add_product1_callbackdata.id)
    assert product1_in_cart != add_product1_callbackdata.get_product_str_for_redis()
    add_product1_callbackdata.quantity += 1
    assert product1_in_cart == add_product1_callbackdata.get_product_str_for_redis()

    await cart.add_product_in_cart(add_product2_callbackdata)
    cart_in_redis = await redis_connection.hgetall(cart.cart_name)
    assert len(cart_in_redis) == 2
    assert cart.items == {
        "1": ProductModel(
            id=1,
            name="test_product_1",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=2,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
        "2": ProductModel(
            id=2,
            name="test_product_2",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=3,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
    }
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
    assert cart.items == {
        "1": ProductModel(
            id=1,
            name="test_product_1",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=3,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
        "2": ProductModel(
            id=2,
            name="test_product_2",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=3,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
    }

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
    assert cart.items == {
        "1": ProductModel(
            id=1,
            name="test_product_1",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=3,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
    }

    string_product_from_redis: str = await redis_connection.hget(cart.cart_name, add_product1_callbackdata.id)
    product_from_redis = AddToCartCallbackFactory.unpack_from_redis(string_product_from_redis)
    assert product_from_redis.quantity == 3

    # А вот тут ни разу не правильная логика получается. Вроде как коллбэк для удаления, а количество увеличивается.
    await cart.change_product_quantity(remove_product1_callbackdata)
    assert cart.items == {
        "1": ProductModel(
            id=1,
            name="test_product_1",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=4,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
    }
    string_product_from_redis: str = await redis_connection.hget(cart.cart_name, remove_product1_callbackdata.id)
    product_from_redis = RemoveFromCartCallbackFactory.unpack_from_redis(string_product_from_redis)
    assert product_from_redis.quantity == 4

    await cart.change_product_quantity(remove_product1_callbackdata, quantity=-3)
    assert cart.items == {
        "1": ProductModel(
            id=1,
            name="test_product_1",
            picture=None,
            description=None,
            category=None,
            price=Decimal("10.00"),
            quantity=1,
            parent_id=None,
            keyboard=None,
            is_data_from_redis=True,
        ),
    }
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

    cart.items = {}
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

    cart_items_in_redis = await redis_connection.hgetall(cart.cart_name)

    assert cart.items != {}
    assert cart_items_in_redis != {}

    await cart.clear()
    cart_items_in_redis = await redis_connection.hgetall(cart.cart_name)

    assert cart.items == {}
    assert cart_items_in_redis == {}


async def test_cart_check_cart_exist(
    cart: Cart,
    add_callbacks: dict[str, AddToCartCallbackFactory],
):
    assert await cart.check_cart_exist() == False

    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()
    await cart.add_product_in_cart(add_product1_callbackdata)
    await cart.add_product_in_cart(add_product2_callbackdata)

    assert await cart.check_cart_exist() == True


async def test_cart_get_cart_info(cart: Cart, add_callbacks: dict[str, AddToCartCallbackFactory]):
    cart_info = await cart.get_cart_info()
    assert cart_info == {"len": 0, "total_cost": 0}

    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()

    await cart.add_product_in_cart(add_product1_callbackdata)
    cart_info = await cart.get_cart_info()
    assert cart_info == {"len": len(cart.items), "total_cost": cart.total_cost}

    await cart.add_product_in_cart(add_product2_callbackdata)
    cart_info = await cart.get_cart_info()

    assert cart_info == {"len": len(cart.items), "total_cost": cart.total_cost}

    await cart.clear()
    cart_info = await cart.get_cart_info()

    assert cart_info == {"len": 0, "total_cost": 0}


async def test_cart_model_dump(cart: Cart, add_callbacks: dict[str, AddToCartCallbackFactory]):
    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()

    dump = cart.model_dump()
    assert dump == {"items": {}, "total_cost": 0}

    await cart.add_product_in_cart(add_product1_callbackdata)
    dump = cart.model_dump()
    assert dump == {
        "items": {
            str(add_product1_callbackdata.id): {
                "product_id": add_product1_callbackdata.id,
                "product_name": add_product1_callbackdata.name,
                "price": add_product1_callbackdata.price,
                "quantity": add_product1_callbackdata.quantity,
                "cost": str(add_product1_callbackdata.cost),
            }
        },
        "total_cost": cart.total_cost,
    }

    await cart.add_product_in_cart(add_product2_callbackdata)
    dump = cart.model_dump()
    assert dump == {
        "items": {
            str(add_product1_callbackdata.id): {
                "product_id": add_product1_callbackdata.id,
                "product_name": add_product1_callbackdata.name,
                "price": add_product1_callbackdata.price,
                "quantity": add_product1_callbackdata.quantity,
                "cost": str(add_product1_callbackdata.cost),
            },
            str(add_product2_callbackdata.id): {
                "product_id": add_product2_callbackdata.id,
                "product_name": add_product2_callbackdata.name,
                "price": add_product2_callbackdata.price,
                "quantity": add_product2_callbackdata.quantity,
                "cost": str(add_product2_callbackdata.cost),
            },
        },
        "total_cost": cart.total_cost,
    }


async def test_cart___len__(cart: Cart, add_callbacks):
    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()

    assert len(cart) == 0

    await cart.add_product_in_cart(add_product1_callbackdata)

    assert len(cart) == add_product1_callbackdata.quantity

    await cart.add_product_in_cart(add_product2_callbackdata)

    assert len(cart) == add_product1_callbackdata.quantity + add_product2_callbackdata.quantity


async def test_cart_total_cost(cart: Cart, add_callbacks):
    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()

    assert cart.total_cost == 0

    await cart.add_product_in_cart(add_product1_callbackdata)

    assert cart.total_cost == add_product1_callbackdata.price * add_product1_callbackdata.quantity

    await cart.add_product_in_cart(add_product2_callbackdata)

    assert (
        cart.total_cost
        == add_product1_callbackdata.price * add_product1_callbackdata.quantity
        + add_product2_callbackdata.price * add_product2_callbackdata.quantity
    )


async def test_cart_get_cart_text(cart: Cart, add_callbacks):
    add_product1_callbackdata, add_product2_callbackdata = add_callbacks.values()

    reference = [
        "`---------------------------------`",
        "`     Товары в вашей корзине      `",
        "`---------------------------------`",
        "`---------------------------------`",
        "`Итог                          0 ₽`",
    ]

    assert cart.get_cart_text() == "\n".join(reference)

    await cart.add_product_in_cart(add_product1_callbackdata)

    reference = [
        "`---------------------------------`",
        "`     Товары в вашей корзине      `",
        "`---------------------------------`",
        "`test_product_1       1    10.00 ₽`",
        "`---------------------------------`",
        "`Итог                      10.00 ₽`",
    ]

    assert cart.get_cart_text() == "\n".join(reference)

    await cart.add_product_in_cart(add_product2_callbackdata)

    reference = [
        "`---------------------------------`",
        "`     Товары в вашей корзине      `",
        "`---------------------------------`",
        "`test_product_1       1    10.00 ₽`",
        "`test_product_2       2    20.00 ₽`",
        "`---------------------------------`",
        "`Итог                      30.00 ₽`",
    ]

    assert cart.get_cart_text() == "\n".join(reference)


def test_cart_get_cart_inline_keyboard(cart: Cart):
    inline_keyboard: InlineKeyboardMarkup = cart.get_cart_inline_keyboard()

    assert isinstance(inline_keyboard, InlineKeyboardMarkup)

    inline_keyboard_buttons: list[list[InlineKeyboardButton]] = cart.get_cart_inline_keyboard().inline_keyboard

    for row in inline_keyboard_buttons:
        for button in row:
            assert isinstance(button, InlineKeyboardButton)

    assert len(inline_keyboard_buttons) == 4

    assert inline_keyboard_buttons[0][0].text == LEXICON_RU["inline"]["add_to_order"]
    assert inline_keyboard_buttons[0][0].callback_data == "make_order"

    assert inline_keyboard_buttons[1][0].text == LEXICON_RU["inline"]["edit_cart"]
    assert inline_keyboard_buttons[1][0].callback_data == EditCartCallbackFactory().pack()

    assert inline_keyboard_buttons[2][0].text == LEXICON_RU["inline"]["clear_cart"]
    assert inline_keyboard_buttons[2][0].callback_data == "clear_cart"

    assert inline_keyboard_buttons[3][0].text == LEXICON_RU["inline"]["checkout"]
    assert inline_keyboard_buttons[3][0].callback_data == "pass"


# async def test_cart__add_cart_button(cart: Cart, products: dict[int, ProductModel]):
#     product_1 = products.get("1")
#     product_1_keyboard_buttons = product_1.keyboard.inline_keyboard
#
#     assert len(product_1_keyboard_buttons) == 3
#     assert len(product_1_keyboard_buttons[0]) == 1
#     assert len(product_1_keyboard_buttons[1]) == 2
#     assert len(product_1_keyboard_buttons[2]) == 1
#
#     product_1_keyboard_buttons = await cart._add_cart_button(product_1_keyboard_buttons)
#
#     assert len(product_1_keyboard_buttons) == 4
#     assert len(product_1_keyboard_buttons[0]) == 1
#     assert len(product_1_keyboard_buttons[1]) == 2
#     assert len(product_1_keyboard_buttons[2]) == 1
#     assert len(product_1_keyboard_buttons[3]) == 1
#
#     cart_info = await cart.get_cart_info()
#
#     assert isinstance(product_1_keyboard_buttons[3][0], InlineKeyboardButton)
#     assert product_1_keyboard_buttons[3][0].text == LEXICON_RU["inline"]["cart"].substitute(
#         total_cost=cart_info["total_cost"],
#         callback_data="cart",
#     )


# async def test_cart__edit_product_button(
#     cart: Cart, products: dict[int, ProductModel], add_callbacks: dict[str, AddToCartCallbackFactory]
# ):
#     product_1 = products.get("1")
#     product_1_keyboard_buttons = product_1.keyboard.inline_keyboard
#
#     assert len(product_1_keyboard_buttons[0]) == 1
#     assert product_1_keyboard_buttons[0][0].text == LEXICON_RU["inline"]["add_cart"]
#     assert product_1_keyboard_buttons[0][0].callback_data == AddToCartCallbackFactory(**product_1.model_dump()).pack()
#
#     product_1_keyboard_buttons = await cart._edit_product_button(product_1_keyboard_buttons)
#
#     assert len(product_1_keyboard_buttons[0]) == 1
#     assert product_1_keyboard_buttons[0][0].text == LEXICON_RU["inline"]["product_quantity_in_cart"].substitute(count=0)
#     assert product_1_keyboard_buttons[0][0].callback_data == AddToCartCallbackFactory(**product_1.model_dump()).pack()
#
#     await cart.add_product_in_cart(add_callbacks["1"])
#
#     product_1_keyboard_buttons = await cart._edit_product_button(product_1_keyboard_buttons)
#
#     assert len(product_1_keyboard_buttons[0]) == 1
#     assert product_1_keyboard_buttons[0][0].text == LEXICON_RU["inline"]["product_quantity_in_cart"].substitute(count=1)
#     assert product_1_keyboard_buttons[0][0].callback_data == AddToCartCallbackFactory(**product_1.model_dump()).pack()


# async def test_cart_get_edit_cart_inline_keyboard(cart: Cart, add_callbacks: dict[str, AddToCartCallbackFactory]):
#
#     def check_inline_keyboard(inline_keyboard: InlineKeyboardMarkup):
#         assert isinstance(inline_keyboard, InlineKeyboardMarkup)
#
#         buttons = inline_keyboard.inline_keyboard
#
#         for row in buttons:
#             for button in row:
#                 assert isinstance(button, InlineKeyboardButton)
#
#         assert len(buttons) == len(cart.items) + 1
#
#     inline_keyboard = await cart.get_edit_cart_inline_keyboard()
#     check_inline_keyboard(inline_keyboard)
#
#     await cart.add_product_in_cart(add_callbacks["1"])
#
#     inline_keyboard = await cart.get_edit_cart_inline_keyboard()
#     check_inline_keyboard(inline_keyboard)
#
#     assert inline_keyboard.inline_keyboard[0][0].text == add_callbacks["1"].name
#     assert (
#         inline_keyboard.inline_keyboard[0][0].callback_data
#         == ProductCallbackFactory(product_id=add_callbacks["1"].id).pack()
#     )
#
#     await cart.add_product_in_cart(add_callbacks["2"])
#
#     inline_keyboard = await cart.get_edit_cart_inline_keyboard()
#     check_inline_keyboard(inline_keyboard)
#
#     assert inline_keyboard.inline_keyboard[1][0].text == add_callbacks["2"].name, "Button 2 text is wrong"
#     assert (
#         inline_keyboard.inline_keyboard[1][0].callback_data
#         == ProductCallbackFactory(product_id=add_callbacks["2"].id).pack()
#     )


# async def test_cart_edit_category_inline_keyboard(cart: Cart, keyboard: InlineKeyboardMarkup):
#     buttons = keyboard.inline_keyboard
#     print(buttons)
#
#     assert len(buttons) == 7
#
#     keyboard = await cart.edit_category_inline_keyboard(buttons)
#     buttons = keyboard.inline_keyboard
#
#     assert len(buttons) == 8


# async def test_cart_edit_product_inline_keyboard(cart: Cart, product_inline_keyboard: InlineKeyboardMarkup):
#     buttons = product_inline_keyboard.inline_keyboard
#     assert len(buttons) == 3
#
#     keyboard = await cart.edit_product_inline_keyboard(buttons)
#     buttons = keyboard.inline_keyboard
#
#     assert len(buttons) == 4

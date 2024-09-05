from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from filters.callback_factories import RemoveFromCartCallbackFactory
from handlers.callback_handlers import remove_from_cart


@pytest.fixture
def remove_from_cart_callback_data():
    yield RemoveFromCartCallbackFactory(
        id=1,
        name="test product",
        price="200.00",
        quantity=1,
        cost="200.00",
    )


@patch("handlers.callback_handlers.Cart")
async def test_remove_from_cart_if_product_not_in_cart(
    Cart_mock: MagicMock,
    callback,
    extra,
    remove_from_cart_callback_data: RemoveFromCartCallbackFactory,
):
    cart = MagicMock()
    cart.get_items_from_redis = AsyncMock()
    cart.remove_product_from_cart = AsyncMock()
    cart.edit_product_inline_keyboard = AsyncMock()
    Cart_mock.return_value = cart

    await remove_from_cart(callback, remove_from_cart_callback_data, extra)

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    cart.get_items_from_redis.assert_called_once()

    cart.remove_product_from_cart.assert_not_called()
    cart.edit_product_inline_keyboard.assert_not_called()
    callback.message.edit_reply_markup.assert_not_called()
    callback.answer.assert_called_once()


@patch("handlers.callback_handlers.Cart")
async def test_remove_from_cart_if_product_in_cart(
    Cart_mock: MagicMock,
    callback,
    extra,
    remove_from_cart_callback_data: RemoveFromCartCallbackFactory,
    product,
):
    cart = MagicMock()
    cart.items = {str(remove_from_cart_callback_data.id): product}
    cart.get_items_from_redis = AsyncMock()
    cart.remove_product_from_cart = AsyncMock()
    cart.edit_product_inline_keyboard = AsyncMock()
    Cart_mock.return_value = cart

    await remove_from_cart(callback, remove_from_cart_callback_data, extra)

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    cart.get_items_from_redis.assert_called_once()

    cart.remove_product_from_cart.assert_called_once()
    cart.edit_product_inline_keyboard.assert_called_once()
    callback.message.edit_reply_markup.assert_called_once()
    callback.answer.assert_called_once()


@patch("handlers.callback_handlers.Cart")
async def test_remove_from_cart_if_product_quantity_is_0(
    Cart_mock: MagicMock,
    callback,
    extra,
    remove_from_cart_callback_data: RemoveFromCartCallbackFactory,
    product,
):
    product.quantity = 0

    cart = MagicMock()
    cart.items = {str(remove_from_cart_callback_data.id): product}
    cart.get_items_from_redis = AsyncMock()
    cart.remove_product_from_cart = AsyncMock()
    cart.edit_product_inline_keyboard = AsyncMock()
    Cart_mock.return_value = cart

    await remove_from_cart(callback, remove_from_cart_callback_data, extra)

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    cart.get_items_from_redis.assert_called_once()

    cart.remove_product_from_cart.assert_not_called()
    cart.edit_product_inline_keyboard.assert_not_called()
    callback.message.edit_reply_markup.assert_not_called()
    callback.answer.assert_called_once()

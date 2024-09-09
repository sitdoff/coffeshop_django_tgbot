from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from filters.callback_factories import AddToCartCallbackFactory
from handlers.callback_handlers import add_to_cart


@pytest.fixture
def add_to_cart_callback_data():
    yield AddToCartCallbackFactory(
        id=1,
        name="test product",
        price="200.00",
        quantity=1,
        cost="200.00",
    )


@patch("handlers.callback_handlers.Cart")
async def test_add_to_cart_if_callback_keyboard_was_edited(
    Cart_mock: MagicMock,
    callback,
    extra,
    add_to_cart_callback_data: AddToCartCallbackFactory,
    cart_mock,
):

    Cart_mock.return_value = cart_mock

    await add_to_cart(callback, add_to_cart_callback_data, extra)

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    cart_mock.add_product_in_cart.assert_called_once()
    cart_mock.add_product_in_cart.assert_awaited()
    cart_mock.add_product_in_cart.assert_called_with(add_to_cart_callback_data)
    cart_mock.edit_product_inline_keyboard.assert_called_once()
    cart_mock.edit_product_inline_keyboard.assert_awaited()
    callback.message.edit_reply_markup.assert_called_once()
    callback.message.edit_reply_markup.assert_awaited()
    callback.answer.assert_called_once()
    callback.answer.assert_awaited()


@patch("handlers.callback_handlers.Cart")
async def test_add_to_cart_if_callback_keyboard_was_not_edited(
    Cart_mock: MagicMock,
    callback,
    extra,
    keyboard,
    add_to_cart_callback_data: AddToCartCallbackFactory,
    cart_mock,
):

    callback.message.reply_markup = keyboard

    Cart_mock.return_value = cart_mock

    await add_to_cart(callback, add_to_cart_callback_data, extra)

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    cart_mock.add_product_in_cart.assert_called_once()
    cart_mock.add_product_in_cart.assert_awaited()
    cart_mock.add_product_in_cart.assert_called_with(add_to_cart_callback_data)
    cart_mock.edit_product_inline_keyboard.assert_called_once()
    cart_mock.edit_product_inline_keyboard.assert_awaited()
    callback.message.edit_reply_markup.assert_not_called()
    callback.answer.assert_called_once()
    callback.answer.assert_awaited()

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import InlineKeyboardMarkup
from filters.callback_factories import ProductCallbackFactory
from handlers.callback_handlers import process_product_callback
from models.cart import Cart
from models.models import ProductModel


@pytest.fixture()
def product_callback_data():
    yield ProductCallbackFactory(product_id=1)


@patch("handlers.callback_handlers.cache_services.save_photo_file_id")
@patch("handlers.callback_handlers.Cart", spec=Cart)
@patch("handlers.callback_handlers.services.edit_product_inline_keyboard")
@patch("handlers.callback_handlers.services.get_product_model_for_answer_callback")
async def test_process_product_callback(
    get_product_model_for_answer_callback_mock: AsyncMock,
    edit_product_inline_keyboard_mock: AsyncMock,
    Cart_mock: MagicMock,
    save_photo_file_id_mock: AsyncMock,
    callback,
    extra,
    product_callback_data,
    cart_mock,
    product1,
):
    get_product_model_for_answer_callback_mock.return_value = product1

    Cart_mock.return_value = cart_mock

    await process_product_callback(callback, extra, product_callback_data)

    get_product_model_for_answer_callback_mock.assert_called_once()
    get_product_model_for_answer_callback_mock.assert_awaited()
    get_product_model_for_answer_callback_mock.assert_called_with(
        callback, extra["api_url"], product_callback_data.product_id
    )

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)

    edit_product_inline_keyboard_mock.assert_called_once()
    edit_product_inline_keyboard_mock.assert_awaited()
    edit_product_inline_keyboard_mock.assert_called_with(cart_mock, keyboard_list=product1.keyboard.inline_keyboard)

    callback.message.edit_media.assert_called_once()
    callback.message.edit_media.assert_awaited()

    save_photo_file_id_mock.assert_called_once()
    save_photo_file_id_mock.assert_awaited()

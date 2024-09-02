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
@patch("handlers.callback_handlers.services.get_product_model_for_answer_callback")
async def test_process_product_callback(
    get_product_model_for_answer_callback_mock: AsyncMock,
    Cart_mock: MagicMock,
    save_photo_file_id_mock: AsyncMock,
    callback,
    extra,
    product_callback_data,
):
    test_product = ProductModel(
        id=1,
        name="test product",
        description="test description",
        category="test category",
        parent_id=1,
        price="20.00",
        quantity=1,
        picture="https://test.com/test.png",
    )
    get_product_model_for_answer_callback_mock.return_value = test_product

    cart = MagicMock()
    cart.edit_product_inline_keyboard = AsyncMock()
    Cart_mock.return_value = cart

    await process_product_callback(callback, extra, product_callback_data)

    get_product_model_for_answer_callback_mock.assert_called_once()
    get_product_model_for_answer_callback_mock.assert_called_with(
        callback, extra["redis_connection"], extra["api_url"], product_callback_data.product_id
    )
    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    cart.edit_product_inline_keyboard.assert_called_once()
    callback.message.edit_media.assert_called_once()
    save_photo_file_id_mock.assert_called_once()

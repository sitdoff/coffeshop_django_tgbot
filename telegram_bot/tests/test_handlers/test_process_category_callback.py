import json
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import InlineKeyboardMarkup
from aioresponses import aioresponses
from filters.callback_factories import CategoryCallbackFactory
from handlers.callback_handlers import process_category_callback
from models.cart import Cart
from models.models import CategoryModel


@patch("handlers.callback_handlers.cache_services.save_photo_file_id")
@patch("handlers.callback_handlers.services.pagination_keyboard")
@patch("handlers.callback_handlers.services.get_category_model_for_answer_callback")
@patch("handlers.callback_handlers.Cart", spec=Cart)
async def test_process_category_callback_without_callback_data(
    Cart_mock: MagicMock,
    get_category_model_for_answer_callback_mock: AsyncMock,
    pagination_keyboard_mock: MagicMock,
    save_photo_file_id_mock: AsyncMock,
    callback,
    extra,
):
    cart = MagicMock()
    cart.edit_category_inline_keyboard = AsyncMock()
    Cart_mock.return_value = cart

    test_category_data = {
        "id": 1,
        "name": "test_name",
        "url": "https://example.com",
        "description": "Test category",
        "picture": None,
        "children": [],
        "products": [],
        "parent": None,
        "parent_id": None,
    }
    test_category = CategoryModel(**test_category_data)
    get_category_model_for_answer_callback_mock.return_value = test_category

    await process_category_callback(callback, extra, None)

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(extra["redis_connection"], callback.from_user.id)
    get_category_model_for_answer_callback_mock.assert_called_once()
    get_category_model_for_answer_callback_mock.assert_called_with(
        callback, extra["redis_connection"], extra["api_url"], None
    )
    pagination_keyboard_mock.assert_called_once()
    pagination_keyboard_mock.assert_called_with(
        keyboard=test_category.keyboard,
        page=1,
        category_id=None,
        factory=CategoryCallbackFactory,
    )
    cart.edit_category_inline_keyboard.assert_called_once()
    callback.message.edit_media.assert_called_once()
    save_photo_file_id_mock.assert_called_once()


@patch("handlers.callback_handlers.cache_services.save_photo_file_id")
@patch("handlers.callback_handlers.services.pagination_keyboard")
@patch("handlers.callback_handlers.services.get_category_model_for_answer_callback")
@patch("handlers.callback_handlers.Cart", spec=Cart)
async def test_process_category_callback_with_callback_data(
    Cart_mock: MagicMock,
    get_category_model_for_answer_callback_mock: AsyncMock,
    pagination_keyboard_mock: MagicMock,
    save_photo_file_id_mock: AsyncMock,
    callback,
    extra,
):
    cart = MagicMock()
    cart.edit_category_inline_keyboard = AsyncMock()
    Cart_mock.return_value = cart

    test_category_data = {
        "id": 1,
        "name": "test_name",
        "url": "https://example.com",
        "description": "Test category",
        "picture": None,
        "children": [],
        "products": [],
        "parent": None,
        "parent_id": None,
    }
    test_category = CategoryModel(**test_category_data)
    get_category_model_for_answer_callback_mock.return_value = test_category

    callback_data = CategoryCallbackFactory(category_id=123, page=22)

    await process_category_callback(callback, extra, callback_data)

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(extra["redis_connection"], callback.from_user.id)
    get_category_model_for_answer_callback_mock.assert_called_once()
    get_category_model_for_answer_callback_mock.assert_called_with(
        callback, extra["redis_connection"], extra["api_url"], callback_data.category_id
    )
    pagination_keyboard_mock.assert_called_once()
    pagination_keyboard_mock.assert_called_with(
        keyboard=test_category.keyboard,
        page=callback_data.page,
        category_id=callback_data.category_id,
        factory=CategoryCallbackFactory,
    )
    cart.edit_category_inline_keyboard.assert_called_once()
    callback.message.edit_media.assert_called_once()
    save_photo_file_id_mock.assert_called_once()

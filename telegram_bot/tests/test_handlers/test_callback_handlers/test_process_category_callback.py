from unittest.mock import AsyncMock, MagicMock, patch

from filters.callback_factories import CategoryCallbackFactory
from handlers.callback_handlers import process_category_callback
from models.cart import Cart
from models.models import CategoryModel


@patch("handlers.callback_handlers.cache_services.save_photo_file_id")
@patch("handlers.callback_handlers.services.pagination_keyboard")
@patch("handlers.callback_handlers.services.edit_category_inline_keyboard")
@patch("handlers.callback_handlers.services.get_category_model_for_answer_callback")
@patch("handlers.callback_handlers.Cart", spec=Cart)
async def test_process_category_callback_without_callback_data(
    Cart_mock: MagicMock,
    get_category_model_for_answer_callback_mock: AsyncMock,
    edit_category_inline_keyboard_mock: AsyncMock,
    pagination_keyboard_mock: MagicMock,
    save_photo_file_id_mock: AsyncMock,
    callback,
    extra,
    cart_mock,
):
    Cart_mock.return_value = cart_mock

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
    Cart_mock.assert_called_with(callback.from_user.id)

    get_category_model_for_answer_callback_mock.assert_called_once()
    get_category_model_for_answer_callback_mock.assert_awaited()
    get_category_model_for_answer_callback_mock.assert_called_with(callback, extra["api_url"], None)

    pagination_keyboard_mock.assert_called_once()
    pagination_keyboard_mock.assert_called_with(
        keyboard=test_category.keyboard,
        page=1,
        category_id=None,
        factory=CategoryCallbackFactory,
    )

    edit_category_inline_keyboard_mock.assert_called_once()
    edit_category_inline_keyboard_mock.assert_awaited()
    edit_category_inline_keyboard_mock.assert_called_with(
        cart=cart_mock, keyboard_list=pagination_keyboard_mock().inline_keyboard
    )

    callback.message.edit_media.assert_called_once()
    callback.message.edit_media.assert_awaited()

    save_photo_file_id_mock.assert_called_once()
    save_photo_file_id_mock.assert_awaited()


@patch("handlers.callback_handlers.cache_services.save_photo_file_id")
@patch("handlers.callback_handlers.services.pagination_keyboard")
@patch("handlers.callback_handlers.services.edit_category_inline_keyboard")
@patch("handlers.callback_handlers.services.get_category_model_for_answer_callback")
@patch("handlers.callback_handlers.Cart", spec=Cart)
async def test_process_category_callback_with_callback_data(
    Cart_mock: MagicMock,
    get_category_model_for_answer_callback_mock: AsyncMock,
    edit_category_inline_keyboard_mock: AsyncMock,
    pagination_keyboard_mock: MagicMock,
    save_photo_file_id_mock: AsyncMock,
    callback,
    extra,
    cart_mock,
):
    Cart_mock.return_value = cart_mock

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
    Cart_mock.assert_called_with(callback.from_user.id)

    get_category_model_for_answer_callback_mock.assert_called_once()
    get_category_model_for_answer_callback_mock.assert_awaited()
    get_category_model_for_answer_callback_mock.assert_called_with(
        callback, extra["api_url"], callback_data.category_id
    )

    pagination_keyboard_mock.assert_called_once()
    pagination_keyboard_mock.assert_called_with(
        keyboard=test_category.keyboard,
        page=callback_data.page,
        category_id=callback_data.category_id,
        factory=CategoryCallbackFactory,
    )

    edit_category_inline_keyboard_mock.assert_called_once()
    edit_category_inline_keyboard_mock.assert_awaited()
    edit_category_inline_keyboard_mock.assert_called_with(
        cart=cart_mock, keyboard_list=pagination_keyboard_mock().inline_keyboard
    )

    callback.message.edit_media.assert_called_once()
    callback.message.edit_media.assert_awaited()

    save_photo_file_id_mock.assert_called_once()
    save_photo_file_id_mock.assert_awaited()

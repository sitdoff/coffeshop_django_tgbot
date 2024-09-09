from unittest.mock import MagicMock, patch

import pytest
from aiogram.types import CallbackQuery
from filters.callback_factories import EditCartCallbackFactory
from handlers.callback_handlers import process_edit_cart_callback


@pytest.fixture
def edit_cart_callback_factory_callback_data():
    yield EditCartCallbackFactory(
        page=1,
    )


@patch("handlers.callback_handlers.services.pagination_keyboard")
@patch("handlers.callback_handlers.Cart")
async def test_process_edit_cart_callback(
    Cart_mock: MagicMock,
    pagination_keyboard_mock: MagicMock,
    callback: CallbackQuery,
    extra: dict,
    cart_mock: MagicMock,
    edit_cart_callback_factory_callback_data: EditCartCallbackFactory,
):
    Cart_mock.return_value = cart_mock

    await process_edit_cart_callback(callback, extra, edit_cart_callback_factory_callback_data)

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    cart_mock.get_items_from_redis.assert_called_once()
    cart_mock.get_edit_cart_inline_keyboard.assert_called_once()
    callback.message.edit_reply_markup.assert_called_once()
    pagination_keyboard_mock.assert_called_once()

from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import CallbackQuery
from handlers.callback_handlers import process_cart_callback


@patch("handlers.callback_handlers.cache_services.save_photo_file_id")
@patch("handlers.callback_handlers.cache_services.get_photo_file_id")
@patch("handlers.callback_handlers.Cart")
async def test_process_cart_callback(
    Cart_mock: MagicMock,
    get_photo_file_id_mock: AsyncMock,
    save_photo_file_id_mock: AsyncMock,
    callback: CallbackQuery,
    extra: dict,
    cart_mock: MagicMock,
):
    Cart_mock.return_value = cart_mock

    await process_cart_callback(callback, extra)

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(user_id=callback.from_user.id)
    cart_mock.get_cart_inline_keyboard.assert_called_once()
    cart_mock.get_items_from_redis.assert_called_once()
    cart_mock.get_items_from_redis.assert_awaited()
    cart_mock.get_cart_text.assert_called_once()
    get_photo_file_id_mock.assert_called_once()
    get_photo_file_id_mock.assert_awaited()
    get_photo_file_id_mock.assert_called_with("cart")
    callback.message.edit_media.assert_called_once()
    callback.message.edit_media.assert_awaited()
    save_photo_file_id_mock.assert_called_once()
    save_photo_file_id_mock.assert_awaited()

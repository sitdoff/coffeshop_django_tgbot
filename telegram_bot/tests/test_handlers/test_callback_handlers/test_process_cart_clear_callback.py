from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import CallbackQuery, FSInputFile
from handlers.callback_handlers import process_cart_clear_callback


@patch("handlers.callback_handlers.cache_services.save_photo_file_id")
@patch("handlers.callback_handlers.get_start_keyboard")
@patch("handlers.callback_handlers.cache_services.get_photo_file_id")
@patch("handlers.callback_handlers.Cart")
async def test_process_cart_clear_callback(
    Cart_mock: MagicMock,
    get_photo_file_id_mock: AsyncMock,
    get_start_keyboard_mock: AsyncMock,
    save_photo_file_id_mock: AsyncMock,
    callback: CallbackQuery,
    extra: dict,
    cart_mock: MagicMock,
):
    Cart_mock.return_value = cart_mock
    get_photo_file_id_mock.return_value = FSInputFile("images/start.jpg")

    await process_cart_clear_callback(callback, extra)

    Cart_mock.assert_called_once()
    Cart_mock.assert_called_with(user_id=callback.from_user.id)
    get_photo_file_id_mock.assert_called_once()
    get_photo_file_id_mock.assert_awaited()
    cart_mock.clear.assert_called_once()
    cart_mock.clear.assert_awaited()
    callback.message.edit_media.assert_called_once()
    callback.message.edit_media.assert_awaited()
    get_photo_file_id_mock.assert_called_once()
    get_photo_file_id_mock.assert_awaited()
    get_start_keyboard_mock.assert_called_once()
    get_start_keyboard_mock.assert_awaited()
    save_photo_file_id_mock.assert_called_once()
    save_photo_file_id_mock.assert_awaited()

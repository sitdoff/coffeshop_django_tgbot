from unittest.mock import AsyncMock, MagicMock, patch

from handlers.command_handlers import process_cart_command
from models.cart import Cart


@patch("handlers.command_handlers.cache_services.save_photo_file_id")
@patch("handlers.command_handlers.cache_services.get_photo_file_id")
@patch("handlers.command_handlers.Cart.get_cart_text")
@patch("handlers.command_handlers.Cart.get_items_from_redis")
@patch("handlers.command_handlers.Cart", spec=Cart)
async def test_process_cart_command(
    Cart_mock: MagicMock,
    cart_get_items_from_redis_mock: AsyncMock,
    cart_get_cart_text_mock: MagicMock,
    get_photo_file_id_mock: AsyncMock,
    save_photo_file_id_mock: AsyncMock,
    message: AsyncMock,
    extra: dict,
):
    cart = MagicMock()
    cart.get_items_from_redis = cart_get_items_from_redis_mock

    cart_get_cart_text_mock.return_value = "caption"
    cart.get_cart_text = cart_get_cart_text_mock

    cart.get_cart_inline_keyboard = MagicMock()
    Cart_mock.return_value = cart

    await process_cart_command(message, extra)

    Cart_mock.assert_called()
    Cart_mock.assert_called_with(message.from_user.id)

    cart.get_items_from_redis.assert_called_once()
    cart.get_items_from_redis.assert_awaited()

    cart.get_cart_text.assert_called_once()

    cart.get_cart_inline_keyboard.assert_called_once()

    get_photo_file_id_mock.assert_called_once()
    get_photo_file_id_mock.assert_called_with(cart_get_cart_text_mock.return_value)
    get_photo_file_id_mock.assert_awaited()

    message.delete.assert_called_once()
    message.delete.assert_awaited()

    message.answer_photo.assert_called_once()
    message.answer_photo.assert_awaited()

    save_photo_file_id_mock.assert_called_once()
    save_photo_file_id_mock.assert_awaited()

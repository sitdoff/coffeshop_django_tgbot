from unittest.mock import AsyncMock, Mock, patch

import pytest
from handlers.command_handlers import process_cart_command


@patch("handlers.command_handlers.cache_services.save_photo_file_id")
@patch("handlers.command_handlers.cache_services.get_photo_file_id")
@patch("handlers.command_handlers.Cart.get_cart_text")
@patch("handlers.command_handlers.Cart.get_items_from_redis")
async def test_process_cart_command(
    cart_get_items_from_redis_mock: AsyncMock,
    cart_get_cart_text_mock: Mock,
    get_photo_file_id_mock: AsyncMock,
    save_photo_file_id_mock: AsyncMock,
    message: AsyncMock,
    extra: dict,
):
    await process_cart_command(message, extra)
    cart_get_items_from_redis_mock.assert_called_once()
    cart_get_items_from_redis_mock.assert_awaited()
    cart_get_cart_text_mock.called == 2
    get_photo_file_id_mock.assert_called_once()
    get_photo_file_id_mock.assert_awaited()
    message.delete.assert_called_once()
    message.delete.assert_awaited()
    message.answer_photo.assert_called_once()
    message.answer_photo.assert_awaited()
    save_photo_file_id_mock.assert_called_once()
    save_photo_file_id_mock.assert_awaited()

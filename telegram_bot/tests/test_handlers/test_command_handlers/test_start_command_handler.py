from unittest.mock import AsyncMock, patch

from aiogram.types import ReplyKeyboardRemove
from aioresponses import aioresponses
from handlers.command_handlers import process_start_command
from lexicon.lexicon_ru import LEXICON_RU


@patch("handlers.command_handlers.get_start_keyboard")
@patch("handlers.command_handlers.services.set_auth_token")
@patch("handlers.command_handlers.services.authorize_user")
@patch("handlers.command_handlers.cache_services.get_photo_file_id")
@patch("handlers.command_handlers.cache_services.save_photo_file_id")
async def test_process_start_command_when_user_not_exist(
    save_photo_file_id_mock: AsyncMock,
    get_photo_file_id_mock: AsyncMock,
    authorize_user_mock: AsyncMock,
    set_auth_token_mock: AsyncMock,
    get_start_keyboard_mock: AsyncMock,
    message: AsyncMock,
    extra: dict,
):
    async def set_auth_token_mock_side_effect(token, message):
        token = "token"
        await extra["redis_connection"].set(f"token:{message.from_user.id}", token)

    set_auth_token_mock.side_effect = set_auth_token_mock_side_effect

    with patch("handlers.command_handlers.get_redis_connection") as mocked_get_redis_connetion:
        mocked_get_redis_connetion.return_value = extra["redis_connection"]
        with aioresponses() as mock_response:
            mock_response.post("http://web:8000/users/create/", status=201, payload={"token": "12345"})
            await process_start_command(message, extra)

    set_auth_token_mock.assert_called()
    set_auth_token_mock.assert_called_with("12345", message)
    set_auth_token_mock.assert_awaited()
    get_photo_file_id_mock.assert_called()
    get_photo_file_id_mock.assert_called_with(LEXICON_RU["commands"]["start"])
    get_photo_file_id_mock.assert_awaited()
    message.answer_photo.assert_called()
    message.answer_photo.assert_awaited()
    get_start_keyboard_mock.assert_called()
    get_start_keyboard_mock.assert_awaited()
    save_photo_file_id_mock.assert_called()
    save_photo_file_id_mock.assert_awaited()

    authorize_user_mock.assert_not_called()
    message.answer.assert_not_called()


@patch("handlers.command_handlers.get_start_keyboard")
@patch("handlers.command_handlers.services.set_auth_token")
@patch("handlers.command_handlers.services.authorize_user")
@patch("handlers.command_handlers.cache_services.get_photo_file_id")
@patch("handlers.command_handlers.cache_services.save_photo_file_id")
async def test_process_start_command_when_user_already_exist(
    save_photo_file_id_mock: AsyncMock,
    get_photo_file_id_mock: AsyncMock,
    authorize_user_mock: AsyncMock,
    set_auth_token_mock: AsyncMock,
    get_start_keyboard_mock: AsyncMock,
    message: AsyncMock,
    extra: dict,
):
    async def authorize_user_mock_side_effect(message, session, api_url):
        token = "token"
        await extra["redis_connection"].set(f"token:{message.from_user.id}", token)

    authorize_user_mock.side_effect = authorize_user_mock_side_effect

    with patch("handlers.command_handlers.aiohttp.client._BaseRequestContextManager") as mock_session_post:
        with patch("handlers.command_handlers.get_redis_connection") as mocked_get_redis_connetion:
            mocked_get_redis_connetion.return_value = extra["redis_connection"]
            with aioresponses() as mock_response:

                async def mock_aenter(*args, **kwargs):
                    return mock_response

                async def mock_aexit(*args, **kwargs):
                    return

                mock_session_post.__aenter__ = mock_aenter
                mock_session_post.__aexit__ = mock_aexit

                mock_response.post("http://web:8000/users/create/", status=400, payload={"token": "12345"})
                await process_start_command(message, extra)

    authorize_user_mock.assert_called()
    authorize_user_mock.assert_awaited()
    get_photo_file_id_mock.assert_called()
    get_photo_file_id_mock.assert_awaited()
    get_photo_file_id_mock.assert_called_with(LEXICON_RU["commands"]["start"])
    message.answer_photo.assert_called()
    message.answer_photo.assert_awaited()
    save_photo_file_id_mock.assert_awaited()

    set_auth_token_mock.assert_not_called()
    message.answer.assert_not_called()


@patch("handlers.command_handlers.services.set_auth_token")
@patch("handlers.command_handlers.services.authorize_user")
@patch("handlers.command_handlers.cache_services.get_photo_file_id")
@patch("handlers.command_handlers.cache_services.save_photo_file_id")
async def test_process_start_command_if_token_not_exist(
    save_photo_file_id_mock: AsyncMock,
    get_photo_file_id_mock: AsyncMock,
    authorize_user_mock: AsyncMock,
    set_auth_token_mock: AsyncMock,
    message: AsyncMock,
    extra: dict,
):
    with patch("handlers.command_handlers.get_redis_connection") as mocked_get_redis_connetion:
        mocked_get_redis_connetion.return_value = extra["redis_connection"]
        with aioresponses() as mock_response:
            mock_response.post("http://web:8000/users/create/", status=None, payload={"token": "12345"})
            await process_start_command(message, extra)

    message.answer.assert_called()
    message.answer.assert_awaited()
    message.answer.assert_called_with(LEXICON_RU["system"]["wrong"], reply_markup=ReplyKeyboardRemove())

    save_photo_file_id_mock.assert_not_called()
    get_photo_file_id_mock.assert_not_called()
    authorize_user_mock.assert_not_called()
    set_auth_token_mock.assert_not_called()

from aiogram.types import Message
from aiohttp import ClientSession
from aioresponses import aioresponses
from services.services import authorize_user, get_auth_token, set_auth_token


async def test_authorize_user_if_token_exists(message: Message, extra: dict):
    token = "token"
    await set_auth_token(token, message, extra["redis_connection"])  # Устанавливаем токен в Redis

    async with ClientSession() as session:
        assert (
            await authorize_user(
                message,
                extra["redis_connection"],
                session,
                extra["api_url"],
            )
            == token
        )


async def test_authorize_user_if_token_not_exists(message: Message, extra: dict):
    token = "token"
    assert await get_auth_token(message, extra["redis_connection"]) is None  # Токена в Redis нет

    with aioresponses() as mock_response:
        async with ClientSession() as session:
            mock_response.post(f"{extra["api_url"]}/users/auth/telegram/", status=200, payload={"token": token})

            assert await authorize_user(message, extra["redis_connection"], session, extra["api_url"]) == token

    assert await get_auth_token(message, extra["redis_connection"]) == token  # Теперь токен есть

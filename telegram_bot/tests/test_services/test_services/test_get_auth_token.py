from unittest.mock import patch

from aiogram.types import Message
from fakeredis.aioredis import FakeRedis
from services.services import get_auth_token
from tests.test_services.events import Events


async def test_get_auth_token_with_message(events: Events, redis_connection: FakeRedis):
    event: Message = events.message
    key = f"token:{event.from_user.id}"
    token = "this_is_token"

    with patch("services.services.get_redis_connection") as get_redis_connection_mock:
        get_redis_connection_mock.return_value = redis_connection
        assert await get_auth_token(event.from_user.id) == None

        await redis_connection.set(key, token)
        await redis_connection.get(key) == token

        assert (await get_auth_token(event.from_user.id)) == token


async def test_get_auth_token_with_callback(events: Events, redis_connection: FakeRedis):
    event: Message = events.callback
    key = f"token:{event.from_user.id}"
    token = "this_is_token"

    with patch("services.services.get_redis_connection") as get_redis_connection_mock:
        get_redis_connection_mock.return_value = redis_connection

        assert await get_auth_token(event.from_user.id) == None

        await redis_connection.set(key, token)

        assert (await get_auth_token(event.from_user.id)) == token

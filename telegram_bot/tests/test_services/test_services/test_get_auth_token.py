from unittest.mock import AsyncMock, patch

from aiogram.types import Message
from conftest import Events
from fakeredis.aioredis import FakeRedis
from redis.asyncio import ConnectionPool
from services.services import get_auth_token


async def test_get_auth_token_with_message(events: Events, redis_connection: FakeRedis):
    event: Message = events.message
    key = f"token:{event.from_user.id}"
    token = "this_is_token"

    with patch("services.services.get_redis_connection") as get_redis_connection_mock:
        get_redis_connection_mock.return_value = redis_connection
        assert await get_auth_token(event) == None

        await redis_connection.set(key, token)
        await redis_connection.get(key) == token

        assert (await get_auth_token(event)) == token


async def test_get_auth_token_with_callback(events: Events, redis_connection: FakeRedis):
    event: Message = events.callback
    key = f"token:{event.from_user.id}"
    token = "this_is_token"

    with patch("services.services.get_redis_connection") as get_redis_connection_mock:
        get_redis_connection_mock.return_value = redis_connection

        assert await get_auth_token(event) == None

        await redis_connection.set(key, token)

        assert (await get_auth_token(event)) == token

from unittest.mock import patch

from aiogram.types import Message
from fakeredis.aioredis import FakeRedis
from services.services import delete_auth_token


async def test_delete_auth_token(message: Message, redis_connection: FakeRedis):
    key = f"token:{message.from_user.id}"
    token = "token"

    with patch("services.services.get_redis_connection") as get_redis_connection_mock:
        get_redis_connection_mock.return_value = redis_connection

        assert await redis_connection.exists(key) == 0

        await redis_connection.set(key, token)

        assert await redis_connection.exists(key) == 1

        await delete_auth_token(message)

        assert await redis_connection.exists(key) == 0

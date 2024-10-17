from aiogram.types import Message
from fakeredis.aioredis import FakeRedis
from services.services import delete_auth_token


async def test_delete_auth_token(message: Message, redis_connection: FakeRedis):
    key = f"token:{message.from_user.id}"
    token = "token"

    assert await redis_connection.exists(key) == 0

    await redis_connection.set(key, token)

    assert await redis_connection.exists(key) == 1

    await delete_auth_token(message, redis_connection)

    assert await redis_connection.exists(key) == 0

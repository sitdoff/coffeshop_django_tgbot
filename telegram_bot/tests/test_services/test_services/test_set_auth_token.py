from aiogram.types import Message
from fakeredis.aioredis import FakeRedis
from services.services import set_auth_token


async def test_set_auth_token(message: Message, redis_connection: FakeRedis):
    message.from_user.id = 1
    key = f"token:{message.from_user.id}"

    assert await redis_connection.exists(key) == 0

    await set_auth_token("token", message, redis_connection)

    assert await redis_connection.exists(key) == 1
    assert await redis_connection.get(key) == "token"

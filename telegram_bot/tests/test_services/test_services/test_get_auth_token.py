from conftest import Events
from fakeredis.aioredis import FakeRedis
from services.services import get_auth_token


async def test_get_auth_token_with_message(events: Events, redis_connection: FakeRedis):
    key = f"token:{events.message.from_user.id}"
    token = "this_is_token"

    assert await get_auth_token(events.message, redis_connection) == None

    await redis_connection.set(key, token)

    assert (await get_auth_token(events.message, redis_connection)).decode() == token


async def test_get_auth_token_with_callback(events: Events, redis_connection: FakeRedis):
    pass

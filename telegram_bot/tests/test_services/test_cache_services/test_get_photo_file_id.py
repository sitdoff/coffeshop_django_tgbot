from aiogram.types import InputMediaPhoto
from config_data import constants
from fakeredis.aioredis import FakeRedis
from services.cache_services import get_photo_file_id


async def test_get_photo_file_id(redis_connection: FakeRedis):
    key = "abcde12345"
    value = "photo_file_id"

    result = await get_photo_file_id(key, redis_connection)

    assert result is None
    await redis_connection.hset(constants.PHOTO_FILE_ID_HASH_NAME, key, value)

    result = await get_photo_file_id(key, redis_connection)
    assert not result is None
    assert isinstance(result, InputMediaPhoto)
    assert result.caption == key
    assert result.media == value

from unittest.mock import patch

from aiogram.types import InputMediaPhoto
from config_data import constants
from fakeredis.aioredis import FakeRedis
from services.cache_services import get_photo_file_id


async def test_get_photo_file_id(redis_connection: FakeRedis):
    key = "abcde12345"
    value = "photo_file_id"

    with patch("services.cache_services.get_redis_connection") as mock_redis_connection:
        mock_redis_connection.return_value = redis_connection
        result = await get_photo_file_id(key)

        assert result is None
        await redis_connection.hset(constants.PHOTO_FILE_ID_HASH_NAME, key, value)

        result = await get_photo_file_id(key)
        assert not result is None
        assert isinstance(result, InputMediaPhoto)
        assert result.caption == key
        assert result.media == value

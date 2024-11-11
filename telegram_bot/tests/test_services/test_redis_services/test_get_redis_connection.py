from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from services.redis_services import get_redis_connection


async def test_get_redis_connection_success():
    mocked_connection = AsyncMock()
    mocked_connection_pool = MagicMock(return_value=mocked_connection)

    with patch("services.redis_services.RedisSengleton.get_pool", return_value=mocked_connection_pool):
        with patch("services.redis_services.Redis", return_value=mocked_connection):
            async with get_redis_connection() as connection:
                assert connection is mocked_connection
            mocked_connection.close.assert_awaited_once()


async def test_get_redis_connection_exception_handling():
    mocked_connection = AsyncMock()
    mocked_connection_pool = MagicMock(return_value=mocked_connection)

    with patch("services.redis_services.RedisSengleton.get_pool", return_value=mocked_connection_pool):
        with patch("services.redis_services.Redis", return_value=mocked_connection):
            async with get_redis_connection() as connection:
                with pytest.raises(ValueError):
                    assert connection is mocked_connection
                    raise ValueError("Test exception")
        mocked_connection.close.assert_awaited_once()

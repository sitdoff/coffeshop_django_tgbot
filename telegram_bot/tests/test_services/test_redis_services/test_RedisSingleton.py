from unittest.mock import MagicMock, patch

from services.redis_services import RedisSengleton


async def test_redis_sengleton():
    redis_singleton_1 = RedisSengleton()
    assert not redis_singleton_1._instance is None

    redis_singleton_2 = RedisSengleton()
    assert redis_singleton_1 is redis_singleton_2


def test_redis_sengleton_init_pool():
    with patch("services.redis_services.ConnectionPool", new_callable=MagicMock()) as mock_connection_pool:
        mock_redis_config = MagicMock()
        mock_redis_config.model_dump.return_value = {
            "host": "localhost",
            "port": 6379,
        }

        redis_singleton = RedisSengleton()
        assert not hasattr(redis_singleton, "_redis_pool")
        pool = redis_singleton.init_pool(mock_redis_config)
        assert hasattr(redis_singleton, "_redis_pool")
        mock_connection_pool.assert_called_once_with(**mock_redis_config.model_dump())
        assert pool == mock_connection_pool.return_value


def test_redis_sengleton_get_pool():
    with patch("services.redis_services.ConnectionPool", new_callable=MagicMock()) as mock_connection_pool:
        mock_redis_config = MagicMock()
        mock_redis_config.model_dump.return_value = {
            "host": "localhost",
            "port": 6379,
        }

        redis_singleton = RedisSengleton()
        assert hasattr(redis_singleton, "_redis_pool")
        assert redis_singleton.get_pool() == redis_singleton._redis_pool

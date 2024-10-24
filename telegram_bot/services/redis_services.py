from config_data.config import RedisConfig
from redis.asyncio import ConnectionPool, Redis


# TODO: Покрыть тестами
class RedisSengleton:
    """
    Класс предоставляет пул соединений с Redis.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisSengleton, cls).__new__(cls)
        return cls._instance

    async def init_pool(self, redis_config: RedisConfig):
        """
        Метод создаёт и возвращает пул соединений.
        """
        if not hasattr(self, "_redis_pool"):
            # TODO: Попробовать сделать так, чтобы можно было просто распаковать словарь из модели конфига
            # примерно так ConnectionPool(**redis_config.dict())
            self._redis_pool = ConnectionPool(host=redis_config.redis_host, port=redis_config.redis_port)
        return self._redis_pool

    async def get_pool(self):
        """
        Метод возвращает уже существующий пул соединений.
        """
        return self._redis_pool


redis_singleton = RedisSengleton()


# TODO: Покрыть тестами
async def get_redis_connection() -> Redis:
    """
    Функция берёт соединение из пула и возвращает его.
    """
    connection_pool: ConnectionPool = await redis_singleton.get_pool()
    connection = await Redis(connection_pool=connection_pool)
    return connection
import logging

from lexicon.lexicon_ru import LEXICON_RU
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class BotConfig(BaseSettings):
    """
    Класс с насроками бота.
    """

    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class ApiConfig(BaseSettings):
    """
    Класс с настройками доступа к API.
    """

    api_protocol: str
    api_host: str
    api_port: int
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def get_api_url(self) -> str:
        return f"{self.api_protocol}://{self.api_host}:{self.api_port}"


class RedisConfig(BaseSettings):
    """
    Класс с настроками доступа к Redis.
    """

    redis_host: str
    redis_port: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class Config(BaseSettings):
    """
    Совокупный класс настроек.
    """

    bot: BotConfig
    api: ApiConfig
    redis: RedisConfig


def load_config() -> Config:
    """
    Возвращает экземпляр класса Config с настройками.
    """
    bot_config = BotConfig()
    logging.info(LEXICON_RU["system"]["bot_config_loaded"])

    api_config = ApiConfig()
    logging.info(LEXICON_RU["system"]["api_config_loaded"])

    redis_config = RedisConfig()
    logging.info(LEXICON_RU["system"]["redis_config_loaded"])

    config = Config(
        bot=bot_config,
        api=api_config,
        redis=redis_config,
    )

    return config

import logging

from lexicon.lexicon_ru import LEXICON_RU
from pydantic import Field
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

    protocol: str
    host: str
    port: int
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="API_",
    )

    def get_api_url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"


class RedisConfig(BaseSettings):
    """
    Класс с настроками доступа к Redis.
    """

    host: str
    port: int
    decode_responses: bool = True
    client_name: str = "telegram_bot_redissengleton"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="REDIS_",
    )


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

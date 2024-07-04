import logging

from lexicon.lexicon_ru import LEXICON_RU
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class BotConfig(BaseSettings):
    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class RedisConfig(BaseSettings):
    redis_password: SecretStr
    redis_host: str
    redis_port: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class Config(BaseSettings):
    bot: BotConfig
    redis: RedisConfig


def load_config() -> Config:
    """
    Creates a class with settings and returns it.
    """
    bot_config = BotConfig()
    logging.info(LEXICON_RU["system"]["bot_config_loaded"])

    redis_config = RedisConfig()
    logging.info(LEXICON_RU["system"]["redis_config_loaded"])

    config = Config(
        bot=bot_config,
        redis=redis_config,
    )

    return config

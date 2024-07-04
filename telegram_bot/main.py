import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from lexicon.lexicon_ru import LEXICON_RU
from redis import Redis

logger = logging.getLogger(__name__)


async def main():
    # Logger basic configuration
    logging.basicConfig(
        level=logging.INFO,
    )

    # Get config.
    config: Config = load_config()
    logging.info(LEXICON_RU["system"]["config_loaded"])

    # Get Redis connection.
    redis_connection: Redis = Redis(
        host=config.redis.redis_host,
        port=config.redis.redis_port,
        password=config.redis.redis_password.get_secret_value(),
    )
    logging.info(LEXICON_RU["system"]["redis_connection_created"])

    # Create Bot
    bot: Bot = Bot(token=config.bot.bot_token.get_secret_value())
    logging.info(LEXICON_RU["system"]["bot_created"])

    # Create Dispatcher.
    dp: Dispatcher = Dispatcher()
    logging.info(LEXICON_RU["system"]["dispatcher_created"])

    # Update workflow data.
    dp.workflow_data.update({"redis": redis_connection})
    logging.info(LEXICON_RU["system"]["workflow_data_updated"])

    # Start polling.
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

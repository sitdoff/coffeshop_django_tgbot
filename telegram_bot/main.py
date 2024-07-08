import asyncio
import logging

import redis
from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import command_handlers
from lexicon.lexicon_ru import LEXICON_RU

logger = logging.getLogger(__name__)


async def main():
    # Logger basic configuration
    logging.basicConfig(
        level=logging.DEBUG,
    )

    # Get config.
    config: Config = load_config()
    logging.info(LEXICON_RU["system"]["config_loaded"])

    # Get Redis connection.
    redis_connection: redis.Redis = redis.Redis(
        host=config.redis.redis_host,
        port=config.redis.redis_port,
        decode_responses=True,
    )
    logging.info(f"Ping Redis: {redis_connection.ping()}")
    logging.info(LEXICON_RU["system"]["redis_connection_created"])

    # Create Bot
    bot: Bot = Bot(token=config.bot.bot_token.get_secret_value())
    logging.info(LEXICON_RU["system"]["bot_created"])

    # Create Dispatcher.
    dp: Dispatcher = Dispatcher()
    logging.info(LEXICON_RU["system"]["dispatcher_created"])

    # Register routers.
    dp.include_router(command_handlers.router)
    logging.info(LEXICON_RU["system"]["routers_registred"])

    # Update workflow data.
    dp.workflow_data.update({"redis_connection": redis_connection})
    dp.workflow_data.update({"api_url": config.api.get_api_url()})
    logging.info(LEXICON_RU["system"]["workflow_data_updated"])

    # Start polling.
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

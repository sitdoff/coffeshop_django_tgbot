import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config_data.config import Config, load_config
from handlers import callback_handlers, command_handlers
from keyboards.set_main_menu import set_main_menu
from lexicon.lexicon_ru import LEXICON_RU
from services.redis_services import get_redis_connection, redis_singleton

logger = logging.getLogger(__name__)


async def main():
    # Logger basic configuration
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(funcName)s:%(message)s",
        level=logging.DEBUG,
    )

    # Get config.
    config: Config = load_config()
    logging.info(LEXICON_RU["system"]["config_loaded"])

    # Init redis connection pool.
    redis_singleton.init_pool(config.redis)
    async with get_redis_connection() as redis_connection:
        ping_redis_result = await redis_connection.ping()
        assert ping_redis_result is True
        logging.info(f"Ping Redis: {ping_redis_result}")
    logging.info(LEXICON_RU["system"]["redis_pool_created"])

    # Create Bot
    bot: Bot = Bot(
        token=config.bot.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode="MarkdownV2"),
    )
    logging.info(LEXICON_RU["system"]["bot_created"])

    # Create Dispatcher.
    dp: Dispatcher = Dispatcher()
    logging.info(LEXICON_RU["system"]["dispatcher_created"])

    # Register routers.
    dp.include_router(command_handlers.router)
    dp.include_router(callback_handlers.router)
    logging.info(LEXICON_RU["system"]["routers_registred"])

    # Update workflow data.
    dp.workflow_data.update(
        {
            "extra": {
                "api_url": config.api.get_api_url(),
            }
        }
    )
    logging.info(LEXICON_RU["system"]["workflow_data_updated"])

    # Install main menu.
    await set_main_menu(bot)
    logging.info(LEXICON_RU["system"]["main_menu_set"])

    # Start polling.
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from lexicon.lexicon_ru import LEXICON_RU

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
    )

    config: Config = load_config()
    logging.info(LEXICON_RU["system"]["config_loaded"])

    bot: Bot = Bot(token=config.bot.bot_token.get_secret_value())
    logging.info(LEXICON_RU["system"]["bot_created"])

    dp: Dispatcher = Dispatcher()
    logging.info(LEXICON_RU["system"]["dispatcher_created"])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

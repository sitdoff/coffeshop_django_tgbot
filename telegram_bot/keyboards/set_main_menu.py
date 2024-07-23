from aiogram import Bot
from aiogram.types import BotCommand
from lexicon.lexicon_ru import LEXICON_MAIN_MENU_RU


async def set_main_menu(bot: Bot):
    """
    Создает и устанавливаен главное меню бота.
    """
    main_menu_commands = [BotCommand(command=key, description=value) for key, value in LEXICON_MAIN_MENU_RU.items()]
    await bot.set_my_commands(main_menu_commands)

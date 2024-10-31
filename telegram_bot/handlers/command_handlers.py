import logging
from typing import Any, Literal

import aiohttp
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, Message, ReplyKeyboardRemove
from keyboards.callback_keyboards import get_start_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from models.cart import Cart
from services import cache_services, services
from services.redis_services import get_redis_connection

router: Router = Router()

logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def process_start_command(
    message: Message,
    extra: dict[Literal["api_url"], Any],
):
    """
    Хэндлер для обработки команды /start.
    """
    payload = {"telegram_id": message.from_user.id, "username": message.from_user.username}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{extra['api_url']}/users/create/", data=payload) as response:
            response_data = await response.json()
            logger.debug(f"Response status: {response.status}, response data: {response_data}")

        if response.status == 201:
            await services.set_auth_token(response_data["token"], message.from_user.id)
            logger.info("Successfully. The user has been created.")
        if response.status == 400:
            await services.authorize_user(message, session, extra["api_url"])
            logger.info(f"Unsuccessful. Error message: {response_data.get('error')}")

    async with get_redis_connection() as redis_connection:
        token = await redis_connection.get(f"token:{message.from_user.id}")

    logger.debug(f"User: {message.from_user.username}:{message.from_user.id}. Auth token: {token}")

    if token:
        photo = await cache_services.get_photo_file_id(LEXICON_RU["commands"]["start"]) or FSInputFile(
            "images/welcome.jpg"
        )
        event = await message.answer_photo(
            photo=photo,
            caption=LEXICON_RU["commands"]["start"],
            reply_markup=await get_start_keyboard(),
        )
        # logger.debug("Message is %s", message)
        await cache_services.save_photo_file_id(event)
    else:
        logger.error(f"User {message.from_user.username}:{message.from_user.id} can't start bot. Token is {token}.")
        await message.answer(LEXICON_RU["system"]["wrong"], reply_markup=ReplyKeyboardRemove())


@router.message(Command(commands=["help"]))
async def process_help_command(message: Message):
    """
    Хэндлер для обработки команды /help.
    """
    await message.answer(LEXICON_RU["commands"]["help"])


@router.message(Command(commands=["cart"]))
async def process_cart_command(message: Message, extra: dict[str, Any]):
    """
    Хэндлер для обработки команды /cart.
    """
    cart = Cart(user_id=message.from_user.id)
    await cart.get_items_from_redis()
    caption = cart.get_cart_text()
    photo = await cache_services.get_photo_file_id(caption) or FSInputFile("images/cart.jpg")
    await message.delete()
    event = await message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=cart.get_cart_inline_keyboard(),
    )
    await cache_services.save_photo_file_id(event)

import logging

import aiohttp
import redis
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from keyboards.callback_keyboards import set_start_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from services import services

router: Router = Router()

logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def process_start_command(message: Message, redis_connection: redis.Redis, api_url: str):
    payload = {"telegram_id": message.from_user.id, "username": message.from_user.username}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/users/create/", data=payload) as response:
            response_data = await response.json()
            logger.debug(f"Response status: {response.status}, response data: {response_data}")

        if response.status == 201:
            services.set_auth_token(response_data["token"], message, redis_connection)
            logger.debug("Successfully. The user has been created.")
        if response.status == 400:
            await services.authorize_user(message, redis_connection, session, api_url)
            logger.debug(f"Unsuccessful. Error message: {response_data.get('error')}")

    token = redis_connection.get(f"token:{message.from_user.id}")
    logger.debug(f"User: {message.from_user.username}:{message.from_user.id}. Auth token: {token}")

    if token:
        await message.answer(LEXICON_RU["commands"]["start"], reply_markup=await set_start_keyboard())
    else:
        logger.error(f"User {message.from_user.username}:{message.from_user.id} can't start bot. Token is {token}.")
        await message.answer(LEXICON_RU["system"]["wrong"])


@router.message(Command(commands=["help"]))
async def process_help_command(message: Message):
    await message.answer(LEXICON_RU["commands"]["help"])

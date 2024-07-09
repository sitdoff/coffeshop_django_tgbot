import logging

import aiohttp
import redis
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from keyboards.callback_keyboards import get_categories_inline_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from services import services

logger = logging.getLogger(__name__)


def set_auth_token(token: str, message: Message, redis_connection: redis.Redis) -> None:
    redis_connection.set(f"token:{message.from_user.id}", token)


def get_auth_token(message: Message, redis_connection: redis.Redis) -> str:
    return redis_connection.get(f"token:{message.from_user.id}")


def delete_auth_token(message: Message, redis_connection: redis.Redis) -> None:
    redis_connection.delete(f"token:{message.from_user.id}")


async def authorize_user(
    message: Message, redis_connection: redis.Redis, session: aiohttp.ClientSession, api_url: str
) -> str:
    token = get_auth_token(message, redis_connection)
    if not token:
        async with session.post(
            f"{api_url}/users/auth/telegram/",
            json={"telegram_id": message.from_user.id},
        ) as response:
            response_data = await response.json()
            token = response_data["token"]
            set_auth_token(token, message, redis_connection)
    return token


async def get_data_for_answer_category_callback(
    callback,
    redis_connection: redis.Redis,
    api_url: str,
    category_id: str | None = None,
) -> tuple[str | InlineKeyboardMarkup] | None:
    if category_id:
        url = f"{api_url}/categories/{category_id}/"
    else:
        url = f"{api_url}/categories/"
    logger.debug("Url is %s", url)

    headers = {
        "Authorization": f"Token {services.get_auth_token(callback, redis_connection)}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                logger.debug("Response data is %s", data)
            else:
                logger.error(LEXICON_RU["system"]["wrong"])
                logger.debug("Response status is %s", response.status)
                return

    description = f"Category {data['name']}"
    keyboard: InlineKeyboardMarkup = await get_categories_inline_keyboard(data)
    return (description, keyboard)

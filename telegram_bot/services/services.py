import logging

import aiohttp
import redis.asyncio as redis
from aiogram.types import FSInputFile, InputMediaPhoto, Message, URLInputFile
from keyboards.callback_keyboards import (
    get_categories_inline_keyboard,
    get_product_inline_keyboard,
)
from lexicon.lexicon_ru import LEXICON_RU
from models.models import CategoryModel, ProductModel

logger = logging.getLogger(__name__)


async def set_auth_token(token: str, message: Message, redis_connection: redis.Redis) -> None:
    await redis_connection.set(f"token:{message.from_user.id}", token)


async def get_auth_token(message: Message, redis_connection: redis.Redis) -> str:
    return await redis_connection.get(f"token:{message.from_user.id}")


async def delete_auth_token(message: Message, redis_connection: redis.Redis) -> None:
    await redis_connection.delete(f"token:{message.from_user.id}")


async def get_picture(data: dict) -> InputMediaPhoto:
    if data["picture"] is None:
        return InputMediaPhoto(media=FSInputFile("images/default.jpg"))
    return InputMediaPhoto(media=URLInputFile(data["picture"]))


async def authorize_user(
    message: Message, redis_connection: redis.Redis, session: aiohttp.ClientSession, api_url: str
) -> str:
    token = await get_auth_token(message, redis_connection)
    if not token:
        async with session.post(
            f"{api_url}/users/auth/telegram/",
            json={"telegram_id": message.from_user.id},
        ) as response:
            response_data = await response.json()
            token = response_data["token"]
            await set_auth_token(token, message, redis_connection)
    return token


async def get_category_model_for_answer_callback(
    callback,
    redis_connection: redis.Redis,
    api_url: str,
    category_id: str | int | None = None,
) -> CategoryModel:
    if category_id:
        url = f"{api_url}/categories/{category_id}/"
    else:
        url = f"{api_url}/categories/"
    logger.debug("Url is %s", url)

    headers = {
        "Authorization": f"Token {await get_auth_token(callback, redis_connection)}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, raise_for_status=True) as response:
            response_data = await response.json()
            logger.debug("Response data is %s", response_data)

    category = CategoryModel(**response_data)

    return category


async def get_product_model_for_answer_callback(
    callback,
    redis_connection: redis.Redis,
    api_url: str,
    product_id: str | int | None,
) -> ProductModel:
    url = f"{api_url}/product/{product_id}/"
    logger.debug("Url is %s", url)

    headers = {
        "Authorization": f"Token {await get_auth_token(callback, redis_connection)}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, raise_for_status=True) as response:
            response_data = await response.json()
            logger.debug("Response data is %s", response_data)

    product = ProductModel(**response_data)

    return product

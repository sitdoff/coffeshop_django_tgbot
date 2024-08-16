import logging
import math

import aiohttp
import redis.asyncio as redis
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    URLInputFile,
)
from config_data import constants
from filters.callback_factories import CategoryCallbackFactory, EditCartCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from models.models import CategoryModel, ProductModel

logger = logging.getLogger(__name__)


async def set_auth_token(token: str, message: Message, redis_connection: redis.Redis) -> None:
    """
    Записывает токен аутентификации в Redis.
    """
    await redis_connection.set(f"token:{message.from_user.id}", token)


async def get_auth_token(message: Message | CallbackQuery, redis_connection: redis.Redis) -> str:
    """
    Возвращает токен аутентификации из Redis.
    """
    return await redis_connection.get(f"token:{message.from_user.id}")


async def delete_auth_token(message: Message, redis_connection: redis.Redis) -> None:
    """
    Удаляет токен аутентификации из Redis.
    """
    await redis_connection.delete(f"token:{message.from_user.id}")


async def authorize_user(
    message: Message, redis_connection: redis.Redis, session: aiohttp.ClientSession, api_url: str
) -> str:
    """
    Возвращает токен аутентификации.

    Сначала проверяет наличие токена пользователя в Redis. Если его нет в Redis,
    то отправляет запрос API на получение токена. Полученный от API токен записывает в Redis.
    """
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
    callback: CallbackQuery,
    redis_connection: redis.Redis,
    api_url: str,
    category_id: str | int | None = None,
) -> CategoryModel:
    """
    Возвращает модель категории.

    Запрашивает данные категории у API. Из полученных данных создает модель категории.
    """
    if category_id:
        url = f"{api_url}/categories/{category_id}/"
    else:
        url = f"{api_url}/categories/"
    logger.debug("Url is %s", url)

    headers = {
        "Authorization": f"Token {await get_auth_token(callback, redis_connection)}",
    }
    logger.debug("Callback data is %s", callback.data)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, raise_for_status=True) as response:
            response_data = await response.json()
            logger.debug("Response data is %s", response_data)

    photo_file_id = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, response_data.get("name"))
    logger.debug("Photo file id is %s", photo_file_id)
    # logger.debug(await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, response_data.get("name")))
    if not photo_file_id is None:
        response_data["picture"] = photo_file_id

    category = CategoryModel(**response_data)

    return category


async def get_product_model_for_answer_callback(
    callback,
    redis_connection: redis.Redis,
    api_url: str,
    product_id: str | int | None,
) -> ProductModel:
    """
    Возвращает модель товара.

    Запрашивает данные категории у API. Из полученных данных создает модель товара.
    """
    url = f"{api_url}/product/{product_id}/"
    logger.debug("Url is %s", url)

    headers = {
        "Authorization": f"Token {await get_auth_token(callback, redis_connection)}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, raise_for_status=True) as response:
            response_data = await response.json()
            logger.debug("Response data is %s", response_data)

    photo_file_id = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, response_data.get("name"))
    logger.debug("Photo file id is %s", photo_file_id)
    if not photo_file_id is None:
        response_data["picture"] = photo_file_id

    product = ProductModel(**response_data)

    return product


def pagination_keyboard(
    keyboard: InlineKeyboardMarkup, page: int, category_id: int | None, factory: CallbackData
) -> InlineKeyboardMarkup:
    """
    Функция возвращает инлайн-клавиатуру пагинированую на количество кнопок указанных в констате PAGINATION_PAGE_SIZE.

    В клавиатуку добавляются кнопки навигации по страницам.
    """
    logger.debug("Buttons %s", keyboard.inline_keyboard)
    if len(keyboard.inline_keyboard) > constants.PAGINATION_PAGE_SIZE:
        if keyboard.inline_keyboard[-1][0].text == LEXICON_RU["inline"]["back"]:
            back_button = keyboard.inline_keyboard.pop(-1)
        elif factory is EditCartCallbackFactory:
            back_button = keyboard.inline_keyboard.pop(-1)
        else:
            back_button = []
        start_index = (constants.PAGINATION_PAGE_SIZE * page) - constants.PAGINATION_PAGE_SIZE
        end_index = start_index + constants.PAGINATION_PAGE_SIZE
        buttons = keyboard.inline_keyboard[start_index:end_index]
        if not category_id is None:
            navigation_buttons = []
            if page > 1:
                buttont_previous = InlineKeyboardButton(
                    text=LEXICON_RU["inline"]["previous"],
                    callback_data=factory(category_id=category_id, page=page - 1).pack(),
                )
                navigation_buttons.append(buttont_previous)
            if math.ceil(len(keyboard.inline_keyboard) / constants.PAGINATION_PAGE_SIZE) > page:
                buttont_next = InlineKeyboardButton(
                    text=LEXICON_RU["inline"]["next"],
                    callback_data=factory(category_id=category_id, page=page + 1).pack(),
                )
                navigation_buttons.append(buttont_next)
            buttons.append(navigation_buttons)
        else:
            navigation_buttons = []
            if page > 1:
                buttont_previous = InlineKeyboardButton(
                    text=LEXICON_RU["inline"]["previous"],
                    callback_data=factory(page=page - 1).pack(),
                )
                navigation_buttons.append(buttont_previous)
            if math.ceil(len(keyboard.inline_keyboard) / constants.PAGINATION_PAGE_SIZE) > page:
                buttont_next = InlineKeyboardButton(
                    text=LEXICON_RU["inline"]["next"],
                    callback_data=factory(page=page + 1).pack(),
                )
                navigation_buttons.append(buttont_next)
            buttons.append(navigation_buttons)
        buttons.append(back_button)
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


async def get_photo_file_id(key: str, redis_connection: redis.Redis) -> InputMediaPhoto | None:
    result = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, key)
    if not result is None:
        logger.info("File ID found in Redis with key %s", key)
        return InputMediaPhoto(media=result, caption=key)
    logger.info("File ID not found in Redis with key %s", key)
    return None


async def save_photo_file_id(event, redis_connection: redis.Redis):
    key, file_id = False, False
    if isinstance(event, CallbackQuery):
        logger.info("Event is callback query")
        key = event.message.caption
        file_id = event.message.photo[-1].file_id
    elif isinstance(event, Message):
        logger.info("Event is message")
        key = event.caption
        file_id = event.photo[-1].file_id
    logger.debug("Key is %s", key)
    logger.debug("File id is %s", file_id)
    if all([key, file_id]):
        is_key_exist = await redis_connection.hexists(constants.PHOTO_FILE_ID_HASH_NAME, key)
        logger.debug("Is key exist %s", is_key_exist)
        try:
            if not is_key_exist:
                await redis_connection.hset(constants.PHOTO_FILE_ID_HASH_NAME, key, file_id)
                logger.info("File ID saved in Redis with key %s", key)
            else:
                logger.info("Key %s already exists", key)
        except Exception as e:
            logger.error(str(e))
    else:
        logger.error("Key is %s", key)
        logger.error("File id is %s", file_id)
        raise ValueError("No key or photo_file_id")

import logging
import math

import aiohttp
import redis.asyncio as redis
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from config_data import constants
from filters.callback_factories import (
    AddToCartCallbackFactory,
    EditCartCallbackFactory,
    ProductCallbackFactory,
)
from lexicon.lexicon_ru import LEXICON_RU
from models.cart import Cart
from models.models import CategoryModel, ProductModel
from services.redis_services import get_redis_connection

logger = logging.getLogger(__name__)


# TODO: Наверное не стоит передевать всё сообщение. Достаточно только id
async def set_auth_token(token: str, message: Message) -> None:
    """
    Записывает токен аутентификации в Redis.
    """
    # await redis_connection.set(f"token:{message.from_user.id}", token)
    async with get_redis_connection() as redis_connection:
        await redis_connection.set(f"token:{message.from_user.id}", token)


# TODO: Наверное не стоит передевать всё сообщение. Достаточно только id
async def get_auth_token(message: Message | CallbackQuery) -> str:
    """
    Возвращает токен аутентификации из Redis.
    """
    async with get_redis_connection() as redis_connection:
        return await redis_connection.get(f"token:{message.from_user.id}")


# TODO: Наверное не стоит передевать всё сообщение. Достаточно только id
async def delete_auth_token(message: Message) -> None:
    """
    Удаляет токен аутентификации из Redis.
    """
    async with get_redis_connection() as redis_connection:
        await redis_connection.delete(f"token:{message.from_user.id}")


# TODO: Наверное не стоит передевать всё сообщение. Достаточно только id
async def authorize_user(message: Message, session: aiohttp.ClientSession, api_url: str) -> str:
    """
    Возвращает токен аутентификации.

    Сначала проверяет наличие токена пользователя в Redis. Если его нет в Redis,
    то отправляет запрос API на получение токена. Полученный от API токен записывает в Redis.
    """
    token = await get_auth_token(message)
    if not token:
        async with session.post(
            f"{api_url}/users/auth/telegram/",
            json={"telegram_id": message.from_user.id},
        ) as response:
            response_data = await response.json()
            token = response_data["token"]
            await set_auth_token(token, message)
    return token


async def get_category_model_for_answer_callback(
    callback: CallbackQuery,
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
        "Authorization": f"Token {await get_auth_token(callback)}",
    }
    logger.debug("Headers are %s", headers)
    logger.debug("Callback data is %s", callback.data)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, raise_for_status=True) as response:
            response_data = await response.json()
            # logger.debug("Response data is %s", response_data)

    async with get_redis_connection() as redis_connection:
        if await redis_connection.hexists(constants.PHOTO_FILE_ID_HASH_NAME, response_data.get("name")):
            logger.info("Photo file id exists in Redis")
            photo_file_id = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, response_data.get("name"))
            logger.info("Photo file id is %s", photo_file_id)
            response_data["picture"] = photo_file_id

    category = CategoryModel(**response_data)

    return category


async def get_product_model_for_answer_callback(
    callback,
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
        "Authorization": f"Token {await get_auth_token(callback)}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, raise_for_status=True) as response:
            response_data = await response.json()
            logger.debug("Response data is %s", response_data)

    async with get_redis_connection() as redis_connection:
        if await redis_connection.hexists(constants.PHOTO_FILE_ID_HASH_NAME, response_data.get("name")):
            logger.info("Photo file id exists in Redis")
            photo_file_id = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, response_data.get("name"))
            logger.info("Photo file id is %s", photo_file_id)
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


async def _add_cart_button(
    cart: Cart, buttons_list: list[list[InlineKeyboardButton]]
) -> list[list[InlineKeyboardButton]]:
    """
    Функция добавляет кнопку корзины в инлайн-клавиатуру продукта.
    """
    cart_info = await cart.get_cart_info()
    cart_button = InlineKeyboardButton(
        text=LEXICON_RU["inline"]["cart"].substitute(total_cost=cart_info["total_cost"]),
        callback_data="cart",
    )
    buttons_list = [
        inline_button for inline_button in buttons_list if inline_button[0].callback_data != cart_button.callback_data
    ]
    buttons_list.append([cart_button])
    return buttons_list


async def _edit_product_button(
    cart: Cart, buttons_list: list[list[InlineKeyboardButton]]
) -> list[list[InlineKeyboardButton]]:
    """
    Функция добавляет информацию о количестве товара в корзине в инлайн-клавиатуру продукта.
    """
    product_button: InlineKeyboardButton = buttons_list[0][0]
    current_product_id = AddToCartCallbackFactory.unpack(product_button.callback_data).id
    current_product = cart.items.get(str(current_product_id))
    product_button.text = LEXICON_RU["inline"]["product_quantity_in_cart"].substitute(
        count=current_product.quantity if not current_product is None else 0
    )

    return buttons_list


async def edit_category_inline_keyboard(cart, keyboard_list: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    """
    Функция изменяет инлайн-клавиатуру категории, добавляя в неё кнопку корзины и информацию о количетсве товара в корзине.
    """
    keyboard_list = await _add_cart_button(cart=cart, buttons_list=keyboard_list)
    return InlineKeyboardMarkup(inline_keyboard=keyboard_list)


async def edit_product_inline_keyboard(
    cart: Cart, keyboard_list: list[list[InlineKeyboardButton]]
) -> InlineKeyboardMarkup:
    """
    Функция изменяет инлайн-клавиатуру товара, добавляя в неё кнопку корзины и информацию о количетсве товара в корзине.
    """
    keyboard_list = await _add_cart_button(cart=cart, buttons_list=keyboard_list)
    keyboard_list = await _edit_product_button(cart=cart, buttons_list=keyboard_list)
    return InlineKeyboardMarkup(inline_keyboard=keyboard_list)


async def get_edit_cart_inline_keyboard(cart: Cart) -> InlineKeyboardMarkup:
    """
    Функция возвращает инлайн-клавиатуру при редактировании корзины.
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=product.name,
                callback_data=ProductCallbackFactory(product_id=product.id).pack(),
            )
        ]
        for product in cart.items.values()
    ]
    buttons = await _add_cart_button(cart, buttons)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

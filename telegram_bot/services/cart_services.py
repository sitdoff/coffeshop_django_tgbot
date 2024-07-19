import logging
from typing import Any, Literal

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from filters.callback_factories import AddToCartCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from models.cart import Cart
from models.models import ProductModel
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class CartManager:
    def __init__(self, redis_connection: Redis, user_id: int):
        self.redis_connection = redis_connection
        self.user_id = user_id
        self.cart_name = f"cart:{self.user_id}"

    async def add_product_in_redis_cart(self, callback_data: AddToCartCallbackFactory) -> None:
        if await self.redis_connection.hexists(self.cart_name, callback_data.id):
            await self.change_product_quantity(callback_data)
            logger.debug("Product %s incremented in cart", callback_data.name)
        else:
            await self.redis_connection.hset(
                name=self.cart_name,
                key=str(callback_data.id),
                value=callback_data.get_product_str_for_redis(),
            )
            logger.debug("Product % added to cart", callback_data.get_product_str_for_redis())

    async def change_product_quantity(self, callback_data: AddToCartCallbackFactory, quantity_added: int = 1) -> None:
        string_product_from_redis: str = await self.redis_connection.hget(self.cart_name, callback_data.id)
        product_from_redis = AddToCartCallbackFactory.unpack_from_redis(string_product_from_redis)
        product_from_redis.quantity += quantity_added
        await self.redis_connection.hset(
            name=self.cart_name,
            key=callback_data.id,
            value=product_from_redis.get_product_str_for_redis(),
        )

    async def check_cart_exist(self) -> bool:
        if await self.redis_connection.exists(self.cart_name):
            return True
        return False

    def get_product_model_from_redis(self, product_dict: dict) -> ProductModel:
        return ProductModel(**product_dict, is_data_from_redis=True)

    async def get_cart_data_from_redis(self) -> dict:
        return await self.redis_connection.hgetall(self.cart_name)

    async def get_cart_dict(self) -> dict:
        cart_data_from_redis = await self.get_cart_data_from_redis()
        logger.debug("Cart data: %s", cart_data_from_redis)
        cart_dict = {
            key: self.get_product_model_from_redis(
                AddToCartCallbackFactory.unpack_from_redis(product_from_redis).model_dump()
            )
            for key, product_from_redis in cart_data_from_redis.items()
        }
        logger.debug("Cart info: %s", cart_dict)
        return cart_dict

    async def get_cart_from_redis(self) -> Cart:
        cart = Cart(items=await self.get_cart_dict()) if await self.check_cart_exist() else Cart()
        logger.debug("Cart is: %s", cart.model_dump())
        return cart

    async def get_cart_info(self) -> dict[Literal["len", "total_cost"], Any]:
        cart = await self.get_cart_from_redis()
        return {
            "len": len(cart),
            "total_cost": cart.total_cost,
        }

    async def add_cart_button(self, keyboard: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
        cart_info = await self.get_cart_info()
        cart_button = InlineKeyboardButton(
            text=LEXICON_RU["inline"]["cart"].substitute(size=cart_info["len"], total_cost=cart_info["total_cost"]),
            callback_data="pass",
        )
        keyboard = [
            inline_button for inline_button in keyboard if inline_button[0].callback_data != cart_button.callback_data
        ]
        keyboard.append([cart_button])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def edit_product_inline_keyboard(self, keyboard: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
        keyboard = self.add_cart_button(keyboard)

        return keyboard

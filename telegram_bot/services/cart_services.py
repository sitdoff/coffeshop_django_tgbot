import logging
from typing import Any, Literal

from aiogram.types import CallbackQuery
from filters.callback_factories import AddToCartCallbackFactory
from models.cart import Cart
from models.models import ProductModel
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class CartManager:
    def __init__(self, callback: CallbackQuery, callback_data: AddToCartCallbackFactory, redis_connection: Redis):
        self.callback = callback
        self.callback_data = callback_data
        self.redis_connection = redis_connection
        self.cart_name = f"cart:{self.callback.from_user.id}"

    async def add_product_in_redis_cart(
        self,
    ) -> None:
        await self.redis_connection.hset(
            name=self.cart_name,
            key=str(self.callback_data.id),
            value=self.callback_data.get_product_str_for_redis(),
        )
        logger.debug("Product % added to cart", self.callback_data.get_product_str_for_redis())

    async def check_cart_exist(self) -> bool:
        if self.redis_connection.exists(self.cart_name):
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
            key: self.get_product_model_from_redis(AddToCartCallbackFactory.unpack_from_redis(product_str).model_dump())
            for key, product_str in cart_data_from_redis.items()
        }
        logger.debug("Cart info: %s", cart_dict)
        return cart_dict

    async def get_cart_from_redis(self) -> Cart:
        cart = Cart(items=await self.get_cart_dict()) if self.check_cart_exist() else Cart()
        logger.debug("Cart is: %s", cart.model_dump())
        return cart

    async def get_cart_info(self) -> dict[Literal["len", "total_cost"], Any]:
        cart = await self.get_cart_from_redis()
        return {
            "len": len(cart),
            "total_cost": cart.total_cost,
        }

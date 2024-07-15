import logging

from aiogram.types import CallbackQuery
from filters.callback_factories import AddToCartCallbackFactory
from models.models import ProductModel
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


def get_product_dict_from_redis_cart(
    product_str: str, template: str = "id:name:price:quantity:cost", delimeter: str = ":"
) -> dict:
    keys = template.split(delimeter)
    values = product_str.split(delimeter)
    return dict(zip(keys, values))


def get_product_model_from_redis(product_dict: dict) -> ProductModel:
    return ProductModel(**product_dict, is_data_from_redis=True)


class CartManager:
    def __init__(self, callback: CallbackQuery, callback_data: AddToCartCallbackFactory):
        self.callback = callback
        self.callback_data = callback_data

    async def add_product_in_redis_cart(self, redis_connection: Redis) -> None:
        cart_in_redis = f"cart:{self.callback.from_user.id}"
        await redis_connection.hset(
            name=cart_in_redis,
            key=str(self.callback_data.id),
            value=self.callback_data.get_product_str_for_redis(),
        )
        logger.debug("Product % added to cart", self.callback_data.get_product_str_for_redis())

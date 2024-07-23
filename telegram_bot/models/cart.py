import logging
from decimal import Decimal
from typing import Any, Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters.callback_factories import AddToCartCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from models.models import ProductModel
from pydantic import BaseModel, Field
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class Cart(BaseModel):
    items: dict[str | int, ProductModel] = {}
    user_id: int = Field(exclude=True)
    cart_name: str = Field(exclude=True)
    redis_connection: Redis = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, redis_connection: Redis, user_id: int):
        super().__init__(redis_connection=redis_connection, user_id=user_id, cart_name=f"cart:{user_id}")
        self.redis_connection = redis_connection
        self.user_id = user_id
        self.cart_name = f"cart:{self.user_id}"

    @property
    def total_cost(self):
        return sum(Decimal(item.cost) for item in self.items.values())

    async def get_product_model_from_string(self, product_string_from_redis) -> ProductModel:
        product_dict = AddToCartCallbackFactory.unpack_from_redis(product_string_from_redis).model_dump()
        return ProductModel(**product_dict, is_data_from_redis=True)

    #
    async def get_items_from_redis(self) -> dict[str | int, ProductModel]:
        product_strings_from_redis = await self._get_cart_data_from_redis()
        items = {
            key: await self.get_product_model_from_string(value) for key, value in product_strings_from_redis.items()
        }
        self.items = items

    async def save_cart(self) -> None:
        if await self.check_cart_exist():
            for key, value in self.items.items():
                await self.redis_connection.hset(
                    self.cart_name, key, AddToCartCallbackFactory(**value.model_dump()).get_product_str_for_redis()
                )

    async def check_cart_exist(self) -> bool:
        if await self.redis_connection.exists(self.cart_name):
            return True
        return False

    async def add_product_in_cart(self, callback_data: AddToCartCallbackFactory) -> None:
        if await self.redis_connection.hexists(self.cart_name, callback_data.id):
            await self.change_product_quantity(callback_data)
            logger.debug("Product %s incremented in cart", callback_data.name)
            pass
        else:
            await self.redis_connection.hset(
                name=self.cart_name,
                key=str(callback_data.id),
                value=callback_data.get_product_str_for_redis(),
            )
            logger.debug("Product %s added to cart", callback_data.get_product_str_for_redis())

    #
    async def change_product_quantity(self, callback_data: AddToCartCallbackFactory, quantity_added: int = 1) -> None:
        string_product_from_redis: str = await self.redis_connection.hget(self.cart_name, callback_data.id)
        product_from_redis = AddToCartCallbackFactory.unpack_from_redis(string_product_from_redis)
        product_from_redis.quantity += quantity_added
        await self.redis_connection.hset(
            name=self.cart_name,
            key=callback_data.id,
            value=product_from_redis.get_product_str_for_redis(),
        )

    #
    async def _get_cart_data_from_redis(self) -> dict:
        return await self.redis_connection.hgetall(self.cart_name)

    #
    # async def get_cart_dict(self) -> dict:
    #     cart_data_from_redis = await self.get_cart_data_from_redis()
    #     logger.debug("Cart data: %s", cart_data_from_redis)
    #     cart_dict = {
    #         key: self.get_product_model_from_redis(
    #             AddToCartCallbackFactory.unpack_from_redis(product_from_redis).model_dump()
    #         )
    #         for key, product_from_redis in cart_data_from_redis.items()
    #     }
    #     logger.debug("Cart info: %s", cart_dict)
    #     return cart_dict
    #
    # async def get_cart_from_redis(self):
    #     cart = Cart(items=await self.get_cart_dict()) if await self.check_cart_exist() else Cart()
    #     logger.debug("Cart is: %s", cart.model_dump())
    #     return cart
    #
    async def get_cart_info(self) -> dict[Literal["len", "total_cost"], Any]:
        await self.get_items_from_redis()
        return {
            "len": len(self.items),
            "total_cost": self.total_cost,
        }

    async def edit_product_inline_keyboard(
        self, keyboard_list: list[list[InlineKeyboardButton]]
    ) -> InlineKeyboardMarkup:
        await self.get_items_from_redis()
        keyboard_list = await self._add_cart_button(buttons_list=keyboard_list)
        keyboard_list = await self._edit_product_button(keyboard_list)
        return InlineKeyboardMarkup(inline_keyboard=keyboard_list)

    async def _add_cart_button(
        self, buttons_list: list[list[InlineKeyboardButton]]
    ) -> list[list[InlineKeyboardButton]]:
        cart_info = await self.get_cart_info()
        cart_button = InlineKeyboardButton(
            text=LEXICON_RU["inline"]["cart"].substitute(total_cost=cart_info["total_cost"]),
            callback_data="pass",
        )
        buttons_list = [
            inline_button
            for inline_button in buttons_list
            if inline_button[0].callback_data != cart_button.callback_data
        ]
        buttons_list.append([cart_button])
        return buttons_list

    async def _edit_product_button(
        self, buttons_list: list[list[InlineKeyboardButton]]
    ) -> list[list[InlineKeyboardButton]]:
        product_button: InlineKeyboardButton = buttons_list[0][0]
        current_product_id = AddToCartCallbackFactory.unpack(product_button.callback_data).id
        current_product = self.items.get(str(current_product_id))
        product_button.text = (
            LEXICON_RU["inline"]["product_quantity_in_cart"].substitute(count=current_product.quantity)
            if not current_product is None
            else LEXICON_RU["inline"]["add_cart"]
        )

        return buttons_list

    #
    # async def edit_product_inline_keyboard(self, keyboard: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    #     keyboard = self.add_cart_button(keyboard)
    #     return keyboard
    #
    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["items"] = {key: item.model_dump(by_alias=True) for key, item in self.items.items()}
        data["total_cost"] = self.total_cost
        return data

    #
    def __len__(self):
        return sum(item.quantity for item in self.items.values())

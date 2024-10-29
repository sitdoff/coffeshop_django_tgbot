import logging
from decimal import Decimal
from typing import Any, Callable, Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters.callback_factories import (
    AddToCartCallbackFactory,
    EditCartCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from lexicon.lexicon_ru import LEXICON_RU
from models.models import ProductModel
from pydantic import BaseModel, Field
from redis.asyncio import Redis
from services.redis_services import get_redis_connection

logger = logging.getLogger(__name__)


class Cart(BaseModel):
    """
    Класс корзины, которая хранит свои данные в Redis.
    """

    items: dict[str | int, ProductModel] = {}
    user_id: int = Field(exclude=True)
    cart_name: str = Field(exclude=True)
    redis_connection_provider: Callable = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, user_id: int, redis_connection_provider: Callable = get_redis_connection):
        super().__init__(
            user_id=user_id,
            cart_name=f"cart:{user_id}",
            redis_connection_provider=redis_connection_provider,
        )
        self.user_id = user_id
        self.cart_name = f"cart:{self.user_id}"
        self.redis_connection_provider = redis_connection_provider

    @property
    def total_cost(self):
        """
        Свойство возвращает общую стоимость всех товаров в корзине.
        """
        return sum(Decimal(item.cost) for item in self.items.values())

    def get_cart_text(self):
        """
        Метод возвращает текст с информацией о товарах в корзине.
        """
        # Длина строки в мобильном приложении 35 символов.
        line = "`" + "-" * 33 + "`" + "\n"
        text = line
        text += f"`{LEXICON_RU['messages']['cart_text_head']:^33}`\n"
        text += line
        for product in self.items.values():
            text += f"`{product.name:<20s} {product.quantity:^2d} {product.cost:>7} {LEXICON_RU['messages']['rub_symbol']}`\n"
        text += line
        text += f"`{LEXICON_RU['messages']['cart_info']} {self.total_cost:>26} {LEXICON_RU['messages']['rub_symbol']}`"
        return text

    def get_cart_inline_keyboard(self) -> InlineKeyboardMarkup:
        """
        Метод возвращает инлайн-клавиатуру при просмотре содержимого корзины.
        """
        buttons = [
            [
                InlineKeyboardButton(text=LEXICON_RU["inline"]["add_to_order"], callback_data="make_order"),
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON_RU["inline"]["edit_cart"], callback_data=EditCartCallbackFactory().pack()
                ),
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU["inline"]["clear_cart"], callback_data="clear_cart"),
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU["inline"]["checkout"], callback_data="pass"),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    # TODO: Возможно это не метод корзины. Ну или скрытый метод.
    async def get_product_model_from_string(self, product_string_from_redis: str) -> ProductModel:
        """
        Метод преобразовывает сроку с данными из Redis в модель товара.
        """
        product_dict = AddToCartCallbackFactory.unpack_from_redis(product_string_from_redis).model_dump()
        return ProductModel(**product_dict, is_data_from_redis=True)

    async def get_items_from_redis(self) -> None:
        """
        Метод берёт все данные товаров из Redis, преобразовывает их в модели товаров, формирует словарь и присваивает атрибуту items.
        """
        product_strings_from_redis = await self._get_cart_data_from_redis()
        items = {
            key: await self.get_product_model_from_string(value) for key, value in product_strings_from_redis.items()
        }
        self.items = items

    # TODO: Метод вообще не используется нигде.
    async def save_cart(self) -> None:
        """
        Метод сохраняет данные из атрибута items в Redis в виде строк.
        """
        async with self.redis_connection_provider() as redis_connection:
            for key, value in self.items.items():
                await redis_connection.hset(
                    self.cart_name, key, AddToCartCallbackFactory(**value.model_dump()).get_product_str_for_redis()
                )

    async def clear(self) -> None:
        """
        Метод очищает корзину.
        """
        async with self.redis_connection_provider() as redis_connection:
            await redis_connection.delete(self.cart_name)
        await self.get_items_from_redis()

    async def check_cart_exist(self) -> bool:
        """
        Метод проверяет существование в Redis корзины с заданным именем.
        """
        async with self.redis_connection_provider() as redis_connection:
            if await redis_connection.exists(self.cart_name):
                return True
        return False

    async def add_product_in_cart(self, callback_data: AddToCartCallbackFactory) -> None:
        """
        Метод добавляет в корзину новый товар или увеличивает количество уже существующего.
        """
        async with self.redis_connection_provider() as redis_connection:
            # TODO: Возможно стоит выести проверку существования товара в Redis в метод change_product_quantity
            if await redis_connection.hexists(self.cart_name, callback_data.id):
                await self.change_product_quantity(callback_data, quantity=callback_data.quantity)
                logger.debug("Product %s incremented in cart", callback_data.name)
            else:
                await redis_connection.hset(
                    name=self.cart_name,
                    key=str(callback_data.id),
                    value=callback_data.get_product_str_for_redis(),
                )
                logger.debug("Product %s added to cart", callback_data.get_product_str_for_redis())
        await self.get_items_from_redis()

    async def remove_product_from_cart(self, callback_data: RemoveFromCartCallbackFactory) -> None:
        """
        Метод уменьшает количество товара в корзине.
        """
        if int(callback_data.quantity) > 0:
            await self.change_product_quantity(callback_data, quantity=callback_data.quantity * -1)

    async def change_product_quantity(
        self, callback_data: AddToCartCallbackFactory | RemoveFromCartCallbackFactory, quantity: int
    ) -> None:
        """
        Метод изменяет количество товара в корзине. Если по итогу количество становится равно или меньше нуля, то такой товар удаляется из корзины.
        """
        self._validate_callback_data_and_quantity(callback_data, quantity)

        async with self.redis_connection_provider() as redis_connection:
            string_product_from_redis: str = await redis_connection.hget(self.cart_name, callback_data.id)

            if string_product_from_redis is None:
                raise ValueError("Product not exists in cart")

            product_from_redis = callback_data.unpack_from_redis(string_product_from_redis)
            product_from_redis.quantity += quantity
            if product_from_redis.quantity <= 0:
                await redis_connection.hdel(
                    self.cart_name,
                    callback_data.id,
                )
            else:
                await redis_connection.hset(
                    name=self.cart_name,
                    key=callback_data.id,
                    value=product_from_redis.get_product_str_for_redis(),
                )
        await self.get_items_from_redis()

    async def _get_cart_data_from_redis(self) -> dict:
        """
        Метод возвращает словарь со строками из Redis.
        """
        async with self.redis_connection_provider() as redis_connection:
            return await redis_connection.hgetall(self.cart_name)

    async def get_cart_info(self) -> dict[Literal["len", "total_cost"], Any]:
        """
        Метод возвращает словарь со свойствами корзины.
        """
        await self.get_items_from_redis()
        return {
            "len": len(self.items),
            "total_cost": self.total_cost,
        }

    def model_dump(self, **kwargs):
        """
        Метод возвращает данные корзины в виде словаря.
        """
        data = super().model_dump(**kwargs)
        data["items"] = {key: item.model_dump(by_alias=True) for key, item in self.items.items()}
        data["total_cost"] = self.total_cost
        return data

    def __len__(self):
        """
        Метод возвращает общее количетсво товаров в корзине.
        """
        return sum(item.quantity for item in self.items.values())

    @staticmethod
    def _validate_callback_data_and_quantity(
        callback_data: AddToCartCallbackFactory | RemoveFromCartCallbackFactory, quantity: int
    ) -> None:
        # TODO: покрыть тестами
        if isinstance(callback_data, AddToCartCallbackFactory) and quantity < 1:
            raise ValueError("callback_data is AddToCartCallbackFactory, quantity must be positive.")

        if isinstance(callback_data, RemoveFromCartCallbackFactory) and quantity > 0:
            raise ValueError("callback_data is RemoveFromCartCallbackFactory, quantity must be negative.")

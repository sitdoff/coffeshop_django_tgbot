import logging
from decimal import Decimal
from typing import Any, Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters.callback_factories import (
    AddToCartCallbackFactory,
    EditCartCallbackFactory,
    ProductCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from lexicon.lexicon_ru import LEXICON_RU
from models.models import ProductModel
from pydantic import BaseModel, Field
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class Cart(BaseModel):
    """
    Класс корзины, которая хранит свои данные в Redis.
    """

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
            text += f"`{product.name:<20s} {product.quantity:^2d} {product.cost:>7s} {LEXICON_RU['messages']['rub_symbol']}`\n"
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

    async def get_edit_cart_inline_keyboard(self) -> InlineKeyboardMarkup:
        """
        Метод возвращает инлайн-клавиатуру при редактировании корзины.
        """
        buttons = [
            [
                InlineKeyboardButton(
                    text=product.name,
                    callback_data=ProductCallbackFactory(product_id=product.id).pack(),
                )
            ]
            for product in self.items.values()
        ]
        buttons = await self._add_cart_button(buttons)
        return InlineKeyboardMarkup(inline_keyboard=buttons)

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

    async def save_cart(self) -> None:
        """
        Метод сохраняет данные из атрибута items в Redis в виде строк.
        """
        # if await self.check_cart_exist():
        for key, value in self.items.items():
            await self.redis_connection.hset(
                self.cart_name, key, AddToCartCallbackFactory(**value.model_dump()).get_product_str_for_redis()
            )

    async def clear(self) -> None:
        """
        Метод очищает корзину.
        """
        await self.redis_connection.delete(self.cart_name)
        await self.get_items_from_redis()

    async def check_cart_exist(self) -> bool:
        """
        Метод проверяет существование в Redis корзины с заданным именем.
        """
        if await self.redis_connection.exists(self.cart_name):
            return True
        return False

    async def add_product_in_cart(self, callback_data: AddToCartCallbackFactory) -> None:
        """
        Метод добавляет в корзину новый товар или увеличивает количество уже существующего.
        """
        if await self.redis_connection.hexists(self.cart_name, callback_data.id):
            await self.change_product_quantity(callback_data)
            logger.debug("Product %s incremented in cart", callback_data.name)
        else:
            await self.redis_connection.hset(
                name=self.cart_name,
                key=str(callback_data.id),
                value=callback_data.get_product_str_for_redis(),
            )
            logger.debug("Product %s added to cart", callback_data.get_product_str_for_redis())

    async def remove_product_from_cart(self, callback_data: RemoveFromCartCallbackFactory) -> None:
        """
        Метод уменьшает количество товара в корзине.
        """
        if int(callback_data.quantity) > 0:
            await self.change_product_quantity(callback_data, quantity=-1)

    async def change_product_quantity(
        self, callback_data: AddToCartCallbackFactory | RemoveFromCartCallbackFactory, quantity: int = 1
    ) -> None:
        """
        Метод изменяет количество товара в корзине. Если по итогу количество становится равно или меньше нуля, то такой товар удаляется из корзины.
        """
        string_product_from_redis: str = await self.redis_connection.hget(self.cart_name, callback_data.id)
        product_from_redis = AddToCartCallbackFactory.unpack_from_redis(string_product_from_redis)
        product_from_redis.quantity += quantity
        if product_from_redis.quantity <= 0:
            await self.redis_connection.hdel(
                self.cart_name,
                callback_data.id,
            )
        else:
            await self.redis_connection.hset(
                name=self.cart_name,
                key=callback_data.id,
                value=product_from_redis.get_product_str_for_redis(),
            )

    async def _get_cart_data_from_redis(self) -> dict:
        """
        Метод возвращает словарь со строками из Redis.
        """
        return await self.redis_connection.hgetall(self.cart_name)

    async def get_cart_info(self) -> dict[Literal["len", "total_cost"], Any]:
        """
        Метод возвращает словарь со свойствами корзины.
        """
        await self.get_items_from_redis()
        return {
            "len": len(self.items),
            "total_cost": self.total_cost,
        }

    # TODO: Этот метод содержит логике, которая скорее относится к категории, а не к корзине.
    async def edit_category_inline_keyboard(
        self, keyboard_list: list[list[InlineKeyboardButton]]
    ) -> InlineKeyboardMarkup:
        """
        Метод изменяет инлайн-клавиатуру категории, добавляя в неё кнопку корзины и информацию о количетсве товара в корзине.
        """
        await self.get_items_from_redis()  # TODO Если синхронизировать корзину после каждого изменнения её содержимого, то тут можно убрать.
        keyboard_list = await self._add_cart_button(buttons_list=keyboard_list)
        # keyboard_list = await self._edit_product_button(keyboard_list) # TODO: Надо ли это?
        return InlineKeyboardMarkup(inline_keyboard=keyboard_list)

    # TODO: Этот метод содержит логике, которая скорее относится к продукту, а не к корзине.
    async def edit_product_inline_keyboard(
        self, keyboard_list: list[list[InlineKeyboardButton]]
    ) -> InlineKeyboardMarkup:
        """
        Метод изменяет инлайн-клавиатуру товара, добавляя в неё кнопку корзины и информацию о количетсве товара в корзине.
        """
        await self.get_items_from_redis()  # TODO Если синхронизировать корзину после каждого изменнения её содержимого, то тут можно убрать.
        keyboard_list = await self._add_cart_button(buttons_list=keyboard_list)
        keyboard_list = await self._edit_product_button(keyboard_list)
        return InlineKeyboardMarkup(inline_keyboard=keyboard_list)

    # TODO: Переделать метод
    # Этот метод как то не вяжется с логикой корзины.
    # Он изменяет клавиатуру продукта, так что он скорее отностится к продукту, а не к корзине.
    async def _add_cart_button(
        self, buttons_list: list[list[InlineKeyboardButton]]
    ) -> list[list[InlineKeyboardButton]]:
        """
        Метод добавляет кнопку корзины в инлайн-клавиатуру продукта.
        """
        cart_info = await self.get_cart_info()
        cart_button = InlineKeyboardButton(
            text=LEXICON_RU["inline"]["cart"].substitute(total_cost=cart_info["total_cost"]),
            callback_data="cart",
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
        """
        Метод добавляет информацию о количестве товара в корзине в инлайн-клавиатуру продукта.
        """
        product_button: InlineKeyboardButton = buttons_list[0][0]
        current_product_id = AddToCartCallbackFactory.unpack(product_button.callback_data).id
        current_product = self.items.get(str(current_product_id))
        product_button.text = LEXICON_RU["inline"]["product_quantity_in_cart"].substitute(
            count=current_product.quantity if not current_product is None else 0
        )

        return buttons_list

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

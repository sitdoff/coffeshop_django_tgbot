from decimal import Decimal
from logging import getLogger
from typing import Any, Optional

from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    URLInputFile,
)
from filters.callback_factories import (
    AddToCartCallbackFactory,
    CategoryCallbackFactory,
    ProductCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from keyboards.callback_keyboards import set_product_button_text
from lexicon.lexicon_ru import LEXICON_RU
from pydantic import BaseModel, ConfigDict, Field, condecimal

logger = getLogger(__name__)


class ProductModel(BaseModel):
    """
    Модель товара.
    """

    id: int = Field(alias="product_id")
    name: str = Field(alias="product_name")
    picture: InputMediaPhoto | str | None = Field(default=None, exclude=True)
    description: str | None = Field(default=None, exclude=True)
    category: str | None = Field(default=None, exclude=True)
    price: condecimal(gt=1, max_digits=5, decimal_places=2)  # pyright: ignore[reportInvalidTypeForm]
    quantity: int | None = 1
    parent_id: int | None = Field(default=None, exclude=True)
    keyboard: InlineKeyboardMarkup | None = Field(default=None, exclude=True)
    is_data_from_redis: bool = Field(default=False, exclude=True)
    model_config = ConfigDict(populate_by_name=True)

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)

        if not data.get("is_data_from_redis"):
            self.picture = self.get_picture(data)
            self.keyboard = self.get_product_inline_keyboard(data)

    @property
    def cost(self) -> Decimal:
        """
        Свойство возвращает общую стоимость товаров.
        """
        if self.quantity is None:
            return Decimal(self.price)
        return Decimal(self.price) * self.quantity

    def model_dump(self, **kwargs: Any) -> dict:
        """
        Метод возвращает данные товара в виде словаря.
        """
        data = super().model_dump(**kwargs)
        data["cost"] = self.cost
        return data

    def get_product_inline_keyboard(self, data: dict) -> InlineKeyboardMarkup:
        """
        Метод возвращает инлайн-клавиатуру товара.
        """
        buttons = [
            [
                InlineKeyboardButton(
                    text=LEXICON_RU["inline"]["add_cart"],
                    callback_data=AddToCartCallbackFactory(**self.model_dump()).pack(),
                ),
            ],
            [
                InlineKeyboardButton(text="-", callback_data=RemoveFromCartCallbackFactory(**self.model_dump()).pack()),
                InlineKeyboardButton(text="+", callback_data=AddToCartCallbackFactory(**self.model_dump()).pack()),
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON_RU["inline"]["back"],
                    callback_data=(CategoryCallbackFactory(category_id=data.get("parent_id")).pack()),
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    def get_picture(self, data) -> InputMediaPhoto:
        """
        Метод возвращает изображение товара. Если его нет, то возвращает изображение-заглушку.
        """
        if data.get("picture") is None:
            logger.info("Product model: Default image is used. %s", self.name)
            return InputMediaPhoto(media=FSInputFile("images/default.jpg"), caption=self.name)
        if "http" in data["picture"] or "https" in data["picture"]:
            logger.info("Product model: Image from URL is used. %s", self.name)
            return InputMediaPhoto(media=URLInputFile(data["picture"]), caption=self.name)
        logger.info("Product model: Image from Redis is used. %s", self.name)
        return InputMediaPhoto(media=data["picture"], caption=self.name)


class NestedCategoryModel(BaseModel):
    """
    Модель вложенной категории.
    """

    id: int
    name: str
    url: str
    description: str | None
    picture: InputMediaPhoto | str | None


class CategoryModel(BaseModel):
    """
    Модель категории.
    """

    id: int
    name: str
    url: str
    description: str = LEXICON_RU["system"]["not_found"]
    picture: InputMediaPhoto | str | None = LEXICON_RU["system"]["not_found"]
    children: Optional[list[NestedCategoryModel]] = None
    products: Optional[list[ProductModel]] = None
    parent: str | None = None
    parent_id: int | None = None
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[]])

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.picture = self.get_picture(data)
        self.keyboard = self.get_category_inline_keyboard(data)

    def get_category_inline_keyboard(self, data: dict) -> InlineKeyboardMarkup:
        """
        Метод возвращает инлайн-клавиатуру категории.
        """
        buttons = []
        if data:
            if data.get("children"):
                buttons = [
                    [
                        InlineKeyboardButton(
                            text=child_category["name"],
                            callback_data=CategoryCallbackFactory(category_id=child_category["id"]).pack(),
                        )
                    ]
                    for child_category in data["children"]
                ]

            if data.get("products"):
                buttons = [
                    [
                        InlineKeyboardButton(
                            text=set_product_button_text(product),
                            callback_data=ProductCallbackFactory(product_id=product["id"]).pack(),
                        )
                    ]
                    for product in data["products"]
                ]

            if data.get("parent_id"):
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=LEXICON_RU["inline"]["back"],
                            callback_data=CategoryCallbackFactory(category_id=data["parent_id"]).pack(),
                        )
                    ]
                )

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    def get_picture(self, data):
        """
        Метод возвращает изображение категории. Если его нет, то возвращает изображение-заглушку.
        """
        if data.get("picture") is None:
            logger.info("Category model: Default image is used.")
            return InputMediaPhoto(media=FSInputFile("images/default.jpg"), caption=self.name)
        if "http" in data["picture"] or "https" in data["picture"]:
            logger.info("Category model: Image from URL is used.")
            return InputMediaPhoto(media=URLInputFile(data["picture"]), caption=self.name)
        logger.info("Category model: Image from Redis is used.")
        return InputMediaPhoto(media=data["picture"], caption=self.name)

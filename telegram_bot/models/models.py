from decimal import Decimal
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
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductModel(BaseModel):
    """
    Модель товара.
    """

    id: int = Field(alias="product_id")
    name: str = Field(alias="product_name")
    picture: InputMediaPhoto | str | None = Field(default=None, exclude=True)
    description: str | None = Field(default=None, exclude=True)
    category: str | None = Field(default=None, exclude=True)
    price: str
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
    def cost(self) -> str | None:
        """
        Свойство возвращает общую стоимость товаров.
        """
        if self.quantity is None:
            return
        return str(Decimal(self.price) * self.quantity)

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
        if data.get("picture", None) is None:
            return InputMediaPhoto(media=FSInputFile("images/default.jpg"), caption=self.description)
        return InputMediaPhoto(media=URLInputFile(data["picture"]), caption=self.description)


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
    keyboard: InlineKeyboardMarkup | None = None

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.picture = self.get_picture(data)
        self.keyboard = self.get_category_inline_keyboard(data)

    @field_validator("id", mode="before")
    def validate_id(cls, value: Any) -> int:
        """
        Валидатор значения id модели. Строки переводятся в целые числа.
        Если значение нельзя перевести в целое число, то выбрасывается исключение.
        """
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValueError("id must be an integer or a string representing an integer")
        return value

    def get_category_inline_keyboard(self, data: dict):
        """
        Метод возвращает инлайн-клавиатуру категории.
        """
        buttons = []
        if data:
            if data["children"]:
                buttons = [
                    [
                        InlineKeyboardButton(
                            text=child_category["name"],
                            callback_data=CategoryCallbackFactory(category_id=child_category["id"]).pack(),
                        )
                    ]
                    for child_category in data["children"]
                ]

            if data["products"]:
                buttons = [
                    [
                        InlineKeyboardButton(
                            text=set_product_button_text(product),
                            callback_data=ProductCallbackFactory(product_id=product["id"]).pack(),
                        )
                    ]
                    for product in data["products"]
                ]
                pass

            if data["parent_id"]:
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
        if data["picture"] is None:
            return InputMediaPhoto(media=FSInputFile("images/default.jpg"), caption=self.description)
        return InputMediaPhoto(media=URLInputFile(data["picture"]), caption=self.description)

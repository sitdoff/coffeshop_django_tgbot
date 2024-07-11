from decimal import Decimal
from typing import Any, Optional

from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    URLInputFile,
)
from filters.callback_factories import CategoryCallbackFactory, ProductCallbackFactory
from keyboards.callback_keyboards import set_product_button_text
from lexicon.lexicon_ru import LEXICON_RU
from pydantic import BaseModel, ConfigDict, Field


class ProductModel(BaseModel):
    id: int = Field(alias="product_id")
    name: str = Field(alias="product_name")
    picture: InputMediaPhoto | str | None = Field(default=None, exclude=True)
    description: str | None = Field(exclude=True)
    category: str | None = Field(exclude=True)
    price: Decimal
    quantity: int | None = None
    parent_id: int | None = Field(default=None, exclude=True)
    keyboard: InlineKeyboardMarkup | None = Field(default=None, exclude=True)
    model_config = ConfigDict(populate_by_name=True)

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.picture = self.get_picture(data)
        self.keyboard = self.get_product_inline_keyboard(data)

    @property
    def cost(self) -> Decimal | None:
        if self.quantity is None:
            return
        return Decimal(self.price) * self.quantity

    def model_dump(self, **kwargs: Any) -> Any:
        data = super().model_dump(**kwargs)
        data["cost"] = self.cost
        return data

    def get_product_inline_keyboard(self, data: dict) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=LEXICON_RU["inline"]["add_cart"], callback_data="pass")],
            [
                InlineKeyboardButton(
                    text=LEXICON_RU["inline"]["back"],
                    callback_data=CategoryCallbackFactory(category_id=data["parent_id"]).pack(),
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    def get_picture(self, data):
        if data["picture"] is None:
            return InputMediaPhoto(media=FSInputFile("images/default.jpg"), caption=self.description)
        return InputMediaPhoto(media=URLInputFile(data["picture"]), caption=self.description)


class NestedCategoryModel(BaseModel):
    id: int
    name: str
    url: str
    description: str | None
    picture: InputMediaPhoto | str | None


class CategoryModel(BaseModel):
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

    def get_category_inline_keyboard(self, data: dict):
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
        if data["picture"] is None:
            return InputMediaPhoto(media=FSInputFile("images/default.jpg"), caption=self.description)
        return InputMediaPhoto(media=URLInputFile(data["picture"]), caption=self.description)

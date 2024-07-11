import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters.callback_factories import CategoryCallbackFactory, ProductCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU

logger = logging.getLogger(__name__)


def set_product_callback(product_id: int | str) -> str:
    return f"product:{product_id}"


def set_product_button_text(product: dict) -> str:
    return f'{product["name"]} - {product["price"]} руб.'


async def get_start_keyboard() -> InlineKeyboardMarkup:
    make_order_button = InlineKeyboardButton(text=LEXICON_RU["inline"]["make_order"], callback_data="make_order")
    my_orders_button = InlineKeyboardButton(text=LEXICON_RU["inline"]["my_orders"], callback_data="pass")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [make_order_button],
            [my_orders_button],
        ]
    )
    return keyboard


def get_categories_inline_keyboard(data: dict) -> InlineKeyboardMarkup | None:
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


def get_product_inline_keyboard(data: dict) -> InlineKeyboardMarkup | None:
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

import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon_ru import LEXICON_RU

logger = logging.getLogger(__name__)


async def get_start_keyboard() -> InlineKeyboardMarkup:
    make_order_button = InlineKeyboardButton(text=LEXICON_RU["inline"]["make_order"], callback_data="make_order")
    my_orders_button = InlineKeyboardButton(text=LEXICON_RU["inline"]["my_orders"], callback_data="my_orders")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [make_order_button],
            [my_orders_button],
        ]
    )
    return keyboard


async def get_categories_inline_keyboard(data: dict) -> InlineKeyboardMarkup | None:
    buttons = []
    if data:
        if data["children"]:
            buttons = [
                [InlineKeyboardButton(text=child_category["name"], callback_data=str(child_category["id"]))]
                for child_category in data["children"]
            ]

        if data["products"]:
            buttons = []
            pass

        if data["parent_id"]:
            buttons.append([InlineKeyboardButton(text=LEXICON_RU["inline"]["back"], callback_data=data["parent_id"])])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

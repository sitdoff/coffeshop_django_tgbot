import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters.callback_factories import CategoryCallbackFactory, ProductCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU

logger = logging.getLogger(__name__)


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

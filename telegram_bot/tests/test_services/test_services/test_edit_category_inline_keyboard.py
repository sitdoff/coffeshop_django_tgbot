from aiogram.types import InlineKeyboardMarkup
from models.cart import Cart
from services.services import edit_category_inline_keyboard


async def test_cart_edit_category_inline_keyboard(cart: Cart, keyboard: InlineKeyboardMarkup):
    buttons = keyboard.inline_keyboard

    assert len(buttons) == 7

    keyboard = await edit_category_inline_keyboard(cart, buttons)
    buttons = keyboard.inline_keyboard

    assert len(buttons) == 8

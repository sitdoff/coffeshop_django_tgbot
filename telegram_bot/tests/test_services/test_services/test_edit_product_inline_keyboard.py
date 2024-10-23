from aiogram.types import InlineKeyboardMarkup
from models.cart import Cart
from services.services import edit_product_inline_keyboard


async def test_cart_edit_product_inline_keyboard(cart: Cart, product_inline_keyboard: InlineKeyboardMarkup):
    buttons = product_inline_keyboard.inline_keyboard
    assert len(buttons) == 3

    keyboard = await edit_product_inline_keyboard(cart, buttons)
    buttons = keyboard.inline_keyboard

    assert len(buttons) == 4

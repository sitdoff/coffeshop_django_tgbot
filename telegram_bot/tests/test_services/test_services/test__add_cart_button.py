from aiogram.types import InlineKeyboardButton
from lexicon.lexicon_ru import LEXICON_RU
from models.cart import Cart
from models.models import ProductModel
from services.services import _add_cart_button


async def test_cart__add_cart_button(cart: Cart, products: dict[int, ProductModel]):
    product_1 = products.get("1")
    product_1_keyboard_buttons = product_1.keyboard.inline_keyboard

    assert len(product_1_keyboard_buttons) == 3
    assert len(product_1_keyboard_buttons[0]) == 1
    assert len(product_1_keyboard_buttons[1]) == 2
    assert len(product_1_keyboard_buttons[2]) == 1

    product_1_keyboard_buttons = await _add_cart_button(cart, product_1_keyboard_buttons)

    assert len(product_1_keyboard_buttons) == 4
    assert len(product_1_keyboard_buttons[0]) == 1
    assert len(product_1_keyboard_buttons[1]) == 2
    assert len(product_1_keyboard_buttons[2]) == 1
    assert len(product_1_keyboard_buttons[3]) == 1

    cart_info = await cart.get_cart_info()

    assert isinstance(product_1_keyboard_buttons[3][0], InlineKeyboardButton)
    assert product_1_keyboard_buttons[3][0].text == LEXICON_RU["inline"]["cart"].substitute(
        total_cost=cart_info["total_cost"],
        callback_data="cart",
    )

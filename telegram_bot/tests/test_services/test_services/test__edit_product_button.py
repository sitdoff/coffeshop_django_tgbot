from filters.callback_factories import AddToCartCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from models.cart import Cart
from models.models import ProductModel
from services.services import _edit_product_button


async def test_cart__edit_product_button(
    cart: Cart, products: dict[int, ProductModel], add_callbacks: dict[str, AddToCartCallbackFactory]
):
    product_1 = products.get("1")
    product_1_keyboard_buttons = product_1.keyboard.inline_keyboard

    assert len(product_1_keyboard_buttons[0]) == 1
    assert product_1_keyboard_buttons[0][0].text == LEXICON_RU["inline"]["add_cart"]
    assert product_1_keyboard_buttons[0][0].callback_data == AddToCartCallbackFactory(**product_1.model_dump()).pack()

    product_1_keyboard_buttons = await _edit_product_button(cart, product_1_keyboard_buttons)

    assert len(product_1_keyboard_buttons[0]) == 1
    assert product_1_keyboard_buttons[0][0].text == LEXICON_RU["inline"]["product_quantity_in_cart"].substitute(count=0)
    assert product_1_keyboard_buttons[0][0].callback_data == AddToCartCallbackFactory(**product_1.model_dump()).pack()

    await cart.add_product_in_cart(add_callbacks["1"])

    product_1_keyboard_buttons = await _edit_product_button(cart, product_1_keyboard_buttons)

    assert len(product_1_keyboard_buttons[0]) == 1
    assert product_1_keyboard_buttons[0][0].text == LEXICON_RU["inline"]["product_quantity_in_cart"].substitute(count=1)
    assert product_1_keyboard_buttons[0][0].callback_data == AddToCartCallbackFactory(**product_1.model_dump()).pack()

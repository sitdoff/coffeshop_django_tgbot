from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters.callback_factories import AddToCartCallbackFactory, ProductCallbackFactory
from models.cart import Cart
from services.services import get_edit_cart_inline_keyboard


async def test_cart_get_edit_cart_inline_keyboard(cart: Cart, add_callbacks: dict[str, AddToCartCallbackFactory]):

    def check_inline_keyboard(inline_keyboard: InlineKeyboardMarkup):
        assert isinstance(inline_keyboard, InlineKeyboardMarkup)

        buttons = inline_keyboard.inline_keyboard

        for row in buttons:
            for button in row:
                assert isinstance(button, InlineKeyboardButton)

        assert len(buttons) == len(cart.items) + 1

    inline_keyboard = await get_edit_cart_inline_keyboard(cart)
    check_inline_keyboard(inline_keyboard)

    await cart.add_product_in_cart(add_callbacks["1"])

    inline_keyboard = await get_edit_cart_inline_keyboard(cart)
    check_inline_keyboard(inline_keyboard)

    assert inline_keyboard.inline_keyboard[0][0].text == add_callbacks["1"].name
    assert (
        inline_keyboard.inline_keyboard[0][0].callback_data
        == ProductCallbackFactory(product_id=add_callbacks["1"].id).pack()
    )

    await cart.add_product_in_cart(add_callbacks["2"])

    inline_keyboard = await get_edit_cart_inline_keyboard(cart)
    check_inline_keyboard(inline_keyboard)

    assert inline_keyboard.inline_keyboard[1][0].text == add_callbacks["2"].name, "Button 2 text is wrong"
    assert (
        inline_keyboard.inline_keyboard[1][0].callback_data
        == ProductCallbackFactory(product_id=add_callbacks["2"].id).pack()
    )

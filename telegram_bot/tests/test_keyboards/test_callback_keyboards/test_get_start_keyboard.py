from aiogram.types import InlineKeyboardMarkup
from keyboards.callback_keyboards import get_start_keyboard
from lexicon.lexicon_ru import LEXICON_RU


async def test_get_start_keyboard():

    result_keyboard: InlineKeyboardMarkup = await get_start_keyboard()

    assert isinstance(result_keyboard, InlineKeyboardMarkup)
    assert result_keyboard.inline_keyboard[0][0].text == LEXICON_RU["inline"]["make_order"]
    assert result_keyboard.inline_keyboard[0][0].callback_data == "make_order"
    assert result_keyboard.inline_keyboard[1][0].text == LEXICON_RU["inline"]["my_orders"]
    assert result_keyboard.inline_keyboard[1][0].callback_data == "pass"

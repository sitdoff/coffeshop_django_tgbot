from unittest.mock import patch

import pytest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters.callback_factories import CategoryCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from services.services import pagination_keyboard


@pytest.fixture
def keyboard():
    buttons = [
        [InlineKeyboardButton(text="Button 1", callback_data="button_1")],
        [InlineKeyboardButton(text="Button 2", callback_data="button_2")],
        [InlineKeyboardButton(text="Button 3", callback_data="button_3")],
        [InlineKeyboardButton(text="Button 4", callback_data="button_4")],
        [InlineKeyboardButton(text="Button 5", callback_data="button_5")],
        [InlineKeyboardButton(text="Button 6", callback_data="button_6")],
        [InlineKeyboardButton(text=LEXICON_RU["inline"]["back"], callback_data="back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def test_pagination_keyboard_function(keyboard):
    with patch("config_data.constants.PAGINATION_PAGE_SIZE", 2):
        new_keyboard = pagination_keyboard(keyboard=keyboard, page=1, category_id=1, factory=CategoryCallbackFactory)
        assert len(new_keyboard.inline_keyboard) == 2 + 2
        assert len(new_keyboard.inline_keyboard[-2]) == 1
        assert (
            new_keyboard.inline_keyboard[-2][0].callback_data == CategoryCallbackFactory(category_id=1, page=2).pack()
        )
        assert new_keyboard.inline_keyboard[-2][0].text == LEXICON_RU["inline"]["next"]
        assert new_keyboard.inline_keyboard[-1][0].text == LEXICON_RU["inline"]["back"]

    with patch("config_data.constants.PAGINATION_PAGE_SIZE", 1):
        new_keyboard = pagination_keyboard(keyboard=keyboard, page=1, category_id=1, factory=CategoryCallbackFactory)
        assert len(new_keyboard.inline_keyboard) == 1 + 2


def test_pagination_keyboard_function_navigation_buttons(keyboard):
    with patch("config_data.constants.PAGINATION_PAGE_SIZE", 2):
        new_keyboard = pagination_keyboard(keyboard=keyboard, page=2, category_id=1, factory=CategoryCallbackFactory)
        assert len(new_keyboard.inline_keyboard) == 2 + 2
        assert len(new_keyboard.inline_keyboard[-2]) == 2
        assert (
            new_keyboard.inline_keyboard[-2][0].callback_data == CategoryCallbackFactory(category_id=1, page=1).pack()
        )
        assert (
            new_keyboard.inline_keyboard[-2][1].callback_data == CategoryCallbackFactory(category_id=1, page=3).pack()
        )
        assert new_keyboard.inline_keyboard[-2][0].text == LEXICON_RU["inline"]["previous"]
        assert new_keyboard.inline_keyboard[-2][1].text == LEXICON_RU["inline"]["next"]


def test_pagination_keyboard_function_when_keyboard_size_less_than_constant(keyboard):
    with patch("config_data.constants.PAGINATION_PAGE_SIZE", 7):
        new_keyboard = pagination_keyboard(keyboard=keyboard, page=2, category_id=1, factory=CategoryCallbackFactory)
        assert new_keyboard.inline_keyboard == keyboard.inline_keyboard

    with patch("config_data.constants.PAGINATION_PAGE_SIZE", 10):
        new_keyboard = pagination_keyboard(keyboard=keyboard, page=2, category_id=1, factory=CategoryCallbackFactory)
        assert new_keyboard.inline_keyboard == keyboard.inline_keyboard

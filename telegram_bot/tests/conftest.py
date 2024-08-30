from unittest.mock import AsyncMock

import pytest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, User
from fakeredis import FakeAsyncRedis
from lexicon.lexicon_ru import LEXICON_RU


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


@pytest.fixture
def user():
    test_user = User(id=123456, is_bot=False, first_name="Test", last_name="User", username="test_user")
    yield test_user


@pytest.fixture
def message(user):
    test_message = AsyncMock()
    test_message.from_user = user
    yield test_message


@pytest.fixture
def callback(user, message):
    test_callback = AsyncMock()
    test_callback.from_user = user
    test_callback.message = message
    yield test_callback


@pytest.fixture
def redis_connection():
    async_redis = FakeAsyncRedis()
    yield async_redis


@pytest.fixture
def extra(redis_connection):
    extra_dict = {
        "redis_connection": redis_connection,
        "api_url": "http://web:8000",
    }
    yield extra_dict

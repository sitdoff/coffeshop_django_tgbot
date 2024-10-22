from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest
from aiogram.types import CallbackQuery, Message
from tests.test_models.conftest import category_init_data, product_init_data


@dataclass
class Events:
    def __init__(self, message: Message, callback: CallbackQuery):
        self.message = message
        self.callback = callback


@pytest.fixture
def message():
    msg = MagicMock(spec=Message)
    msg.caption = "message caption"
    msg.photo = [MagicMock()]
    msg.photo[-1].file_id = "message photo id"
    msg.from_user = MagicMock()
    msg.from_user.id = 1
    yield msg


@pytest.fixture
def callback(message: Message):
    cb = MagicMock(spec=CallbackQuery)
    cb.message = message
    cb.from_user = MagicMock()
    cb.from_user.id = 1
    cb.data = "test data"
    yield cb


@pytest.fixture
def events(message: Message, callback: CallbackQuery):
    yield Events(message, callback)

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest
from aiogram.types import CallbackQuery, Message


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
    msg.from_user.id = None
    yield msg


@pytest.fixture
def callback(message: Message):
    cb = MagicMock(spec=CallbackQuery)
    cb.message = message
    yield cb


@pytest.fixture
def events(message: Message, callback: CallbackQuery):
    yield Events(message, callback)

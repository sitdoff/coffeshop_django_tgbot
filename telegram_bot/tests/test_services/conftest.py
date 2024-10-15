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
    yield msg


@pytest.fixture
def callback():
    cb = MagicMock(spec=CallbackQuery)
    cb.message = MagicMock(spec=Message)
    cb.message.caption = "callback caption"
    cb.message.photo = [MagicMock()]
    cb.message.photo[-1].file_id = "callback photo id"
    yield cb


@pytest.fixture
def events(message: Message, callback: CallbackQuery):
    yield Events(message, callback)

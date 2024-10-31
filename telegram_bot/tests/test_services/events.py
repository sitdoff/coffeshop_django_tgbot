from dataclasses import dataclass

from aiogram.types import CallbackQuery, Message


@dataclass
class Events:
    def __init__(self, message: Message, callback: CallbackQuery):
        self.message = message
        self.callback = callback

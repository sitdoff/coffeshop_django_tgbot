import logging

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)


class IsCategoryCallback(BaseFilter):
    def __init__(self, prefix: str):
        self.prefix = prefix

    async def __call__(self, callback: CallbackQuery):
        if callback.data and ":" in callback.data:
            prefix, category_id = callback.data.split(":")
            logger.debug("Filter IsCategoryCallback worked. Prefix: %s, category_id: %s", prefix, category_id)
            return {"category_id": category_id} if prefix == self.prefix else False

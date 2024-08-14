from logging import getLogger
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from config_data.constants import PHOTO_FILE_ID_HASH_NAME

logger = getLogger(__name__)


class SavePhotoFileId(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # logger.debug("Handler is %s", handler)
        # logger.debug("Event is %s", event)
        # logger.debug("Event data is %s", event.data)
        # logger.debug("Data is %s", data)

        await self.save_photo_file_id(event, data)

        result = await handler(event, data)

        return result

    async def save_photo_file_id(self, event: TelegramObject, data: Dict[str, Any]):
        callback_data = event.data
        file_id = event.message.photo[-1].file_id
        redis_connection = data["extra"]["redis_connection"]
        logger.info(
            "File ID %s exists in Redis = %s", file_id, await redis_connection.hexists("photo_file_id", callback_data)
        )
        if not await redis_connection.hexists(PHOTO_FILE_ID_HASH_NAME, callback_data):
            await redis_connection.hset(PHOTO_FILE_ID_HASH_NAME, callback_data, file_id)
            logger.info('File ID "%s" saved to Redis with key "%s"', file_id, callback_data)

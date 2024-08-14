from logging import getLogger
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from config_data.constants import PHOTO_FILE_ID_HASH_NAME
from redis.asyncio import Redis

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
        # logger.debug("Data is %s", data)

        await self.save_photo_file_id(event, data)

        result = await handler(event, data)

        return result

    async def save_photo_file_id(self, event: TelegramObject, data: Dict[str, Any]):
        photo_caption = event.message.caption
        file_id = event.message.photo[-1].file_id
        redis_connection: Redis = data["extra"]["redis_connection"]
        if not await redis_connection.hexists(PHOTO_FILE_ID_HASH_NAME, photo_caption):
            # Тут должен использоваться метод hexpire для установки времени жизни ключа в хэше вместо hset,
            # но он будет доступен только в версии Redis 5.1
            # Сейчас же доступна только версия 5.0.7, так что с этим методом пока облом.
            await redis_connection.hset(PHOTO_FILE_ID_HASH_NAME, photo_caption, file_id)
            logger.info('File ID "%s" saved to Redis with key "%s"', file_id, photo_caption)

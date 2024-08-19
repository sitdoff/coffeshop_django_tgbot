from logging import getLogger
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from config_data import constants
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
        key, file_id = False, False
        redis_connection: Redis = data["extra"]["redis_connection"]
        if isinstance(event, CallbackQuery):
            logger.info("Event is callback query")
            key = event.message.caption
            file_id = event.message.photo[-1].file_id
        else:
            logger.error("Event is not callback query")
            raise ValueError("Event is not callback query")
        logger.debug("Key is %s", key)
        logger.debug("File id is %s", file_id)
        if all([key, file_id]):
            is_key_exist = await redis_connection.hexists(constants.PHOTO_FILE_ID_HASH_NAME, key)
            logger.debug("Is key exist %s", is_key_exist)
            try:
                if not is_key_exist:
                    await redis_connection.hset(constants.PHOTO_FILE_ID_HASH_NAME, key, file_id)
                    logger.info("File ID saved in Redis with key %s", key)
                else:
                    logger.info("Key %s already exists", key)
            except Exception as e:
                logger.error(str(e))
        else:
            logger.error("Key is %s", key)
            logger.error("File id is %s", file_id)
            raise ValueError("No key or photo_file_id")

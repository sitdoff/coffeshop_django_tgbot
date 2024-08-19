import logging

from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from config_data import constants
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


async def get_photo_file_id(key: str, redis_connection: Redis) -> InputMediaPhoto | None:
    result = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, key)
    if not result is None:
        logger.info("File ID found in Redis with key %s", key)
        logger.info("File ID %s got from Redis", result)
        return InputMediaPhoto(media=result, caption=key)
    logger.info("File ID not found in Redis with key %s", key)
    return None


async def save_photo_file_id(event, redis_connection: Redis):
    key, file_id = False, False
    if isinstance(event, CallbackQuery):
        logger.info("Event is callback query")
        key = event.message.caption
        file_id = event.message.photo[-1].file_id
    elif isinstance(event, Message):
        logger.info("Event is message")
        key = event.caption
        file_id = event.photo[-1].file_id
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
        logger.error("No key or photo_file_id")
        raise ValueError("No key or photo_file_id")

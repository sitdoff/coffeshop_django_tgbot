from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from config_data import constants
from conftest import Events
from fakeredis.aioredis import FakeRedis
from services.cache_services import save_photo_file_id


def get_params_form_message(message: Message) -> tuple[Message, str, str]:
    return message, message.caption, message.photo[-1].file_id


async def test_save_photo_file_id_with_message_if_key_none(events: Events, redis_connection: FakeRedis):
    message, caption, file_id = get_params_form_message(events.message)

    photo_file_id_form_redis = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, caption)
    assert photo_file_id_form_redis is None

    await save_photo_file_id(message, redis_connection)

    photo_file_id_form_redis: bytes = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, caption)
    assert not photo_file_id_form_redis is None
    assert photo_file_id_form_redis.decode() == file_id


async def test_save_photo_file_id_with_message_if_key_exists(
    events: dict[str, Message | CallbackQuery], redis_connection: FakeRedis
):
    message, caption, file_id = get_params_form_message(events.message)
    key = "key_for_message_photo_file_id"

    photo_file_id_form_redis = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, key)
    assert photo_file_id_form_redis is None

    await save_photo_file_id(message, redis_connection, key=key)

    photo_file_id_form_redis: bytes = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, key)
    assert not photo_file_id_form_redis is None
    assert photo_file_id_form_redis.decode() == file_id


async def test_save_photo_file_id_with_callback_if_key_none(
    events: dict[str, Message | CallbackQuery], redis_connection: FakeRedis
):
    pass


async def test_save_photo_file_id_with_callback_if_key_exists(
    events: dict[str, Message | CallbackQuery], redis_connection: FakeRedis
):
    pass

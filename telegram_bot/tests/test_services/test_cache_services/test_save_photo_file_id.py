from unittest.mock import patch

import pytest
from aiogram.types import CallbackQuery, Message
from config_data import constants
from conftest import Events
from fakeredis.aioredis import FakeRedis
from services.cache_services import save_photo_file_id


def get_params_form_message(message: Message) -> tuple[Message, str, str]:
    return message, message.caption, message.photo[-1].file_id


def get_params_form_callback(callback: CallbackQuery) -> tuple[CallbackQuery, str, str]:
    return callback, callback.message.caption, callback.message.photo[-1].file_id


async def test_save_photo_file_id_with_message_if_key_is_none(events: Events, redis_connection: FakeRedis):
    with patch("services.cache_services.get_redis_connection", return_value=redis_connection):
        message, caption, file_id = get_params_form_message(events.message)

        photo_file_id_form_redis = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, caption)
        assert photo_file_id_form_redis is None

        await save_photo_file_id(message)

        photo_file_id_form_redis: bytes = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, caption)
        assert not photo_file_id_form_redis is None
        assert photo_file_id_form_redis == file_id


async def test_save_photo_file_id_with_message_if_key_exists(events: Events, redis_connection: FakeRedis):
    with patch("services.cache_services.get_redis_connection", return_value=redis_connection):
        message, _, file_id = get_params_form_message(events.message)
        key = "key_for_message_photo_file_id"

        photo_file_id_form_redis = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, key)
        assert photo_file_id_form_redis is None

        await save_photo_file_id(message, key=key)

        photo_file_id_form_redis: bytes = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, key)
        assert not photo_file_id_form_redis is None
        assert photo_file_id_form_redis == file_id


async def test_save_photo_file_id_with_callback_if_key_is_none(events: Events, redis_connection: FakeRedis):
    with patch("services.cache_services.get_redis_connection", return_value=redis_connection):
        callback, caption, file_id = get_params_form_callback(events.callback)

        photo_file_id_form_redis = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, caption)
        assert photo_file_id_form_redis is None

        await save_photo_file_id(callback)

        photo_file_id_form_redis: bytes = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, caption)
        assert not photo_file_id_form_redis is None
        assert photo_file_id_form_redis == file_id


async def test_save_photo_file_id_with_callback_if_key_exists(events: Events, redis_connection: FakeRedis):
    with patch("services.cache_services.get_redis_connection", return_value=redis_connection):
        callback, _, file_id = get_params_form_callback(events.callback)
        key = "key_for_message_photo_file_id"

        photo_file_id_form_redis = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, key)
        assert photo_file_id_form_redis is None

        await save_photo_file_id(callback, key=key)

        photo_file_id_form_redis: bytes = await redis_connection.hget(constants.PHOTO_FILE_ID_HASH_NAME, key)
        assert not photo_file_id_form_redis is None
        assert photo_file_id_form_redis == file_id


async def test_save_photo_file_id_with_message_if_caption_is_none(events: Events, redis_connection: FakeRedis):
    with patch("services.cache_services.get_redis_connection", return_value=redis_connection):
        events.message.caption = None
        message, caption, _ = get_params_form_message(events.message)

        assert caption is None

        with pytest.raises(ValueError) as exc:
            await save_photo_file_id(message)
        assert "No key or photo_file_id" in str(exc.value)


async def test_save_photo_file_id_with_message_if_file_id_is_none(events: Events, redis_connection: FakeRedis):
    with patch("services.cache_services.get_redis_connection", return_value=redis_connection):
        events.message.photo[-1].file_id = None
        message, _, file_id = get_params_form_message(events.message)

        assert file_id is None

        with pytest.raises(ValueError) as exc:
            await save_photo_file_id(message)
        assert "No key or photo_file_id" in str(exc.value)


async def test_save_photo_file_id_with_callback_if_caption_is_none(events: Events, redis_connection: FakeRedis):
    with patch("services.cache_services.get_redis_connection", return_value=redis_connection):
        events.callback.message.caption = None
        callback, caption, _ = get_params_form_callback(events.callback)

        assert caption is None

        with pytest.raises(ValueError) as exc:
            await save_photo_file_id(callback)
        assert "No key or photo_file_id" in str(exc.value)


async def test_save_photo_file_id_with_callback_if_file_id_is_none(events: Events, redis_connection: FakeRedis):
    with patch("services.cache_services.get_redis_connection", return_value=redis_connection):
        events.callback.message.photo[-1].file_id = None
        callback, _, file_id = get_params_form_callback(events.callback)

        assert file_id is None

        with pytest.raises(ValueError) as exc:
            await save_photo_file_id(callback)
        assert "No key or photo_file_id" in str(exc.value)

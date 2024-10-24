from unittest.mock import patch

from aiogram.types import CallbackQuery
from aioresponses import aioresponses
from models.models import CategoryModel
from services.services import get_category_model_for_answer_callback


async def test_get_category_model_for_answer_callback_if_category_id_is_None(
    callback: CallbackQuery, extra: dict, category_init_data
):

    response_payload = category_init_data

    with aioresponses() as mock_response:
        with patch("services.services.get_redis_connection") as get_redis_connection_mock:
            get_redis_connection_mock.return_value = extra["redis_connection"]

            url = f"{extra['api_url']}/categories/"
            mock_response.get(url, status=200, payload=response_payload)
            result: CategoryModel = await get_category_model_for_answer_callback(callback, extra["api_url"])

    assert isinstance(result, CategoryModel)
    assert result.id == category_init_data["id"]
    assert result.name == category_init_data["name"]
    assert result.url == category_init_data["url"]
    assert result.description == category_init_data["description"]
    assert result.children == category_init_data["children"]
    assert result.products == category_init_data["products"]
    assert result.products == category_init_data["products"]
    assert result.parent_id == category_init_data["parent_id"]


async def test_get_category_model_for_answer_callback(callback: CallbackQuery, extra: dict, category_init_data):
    response_payload = category_init_data

    with aioresponses() as mock_response:
        with patch("services.services.get_redis_connection") as get_redis_connection_mock:
            get_redis_connection_mock.return_value = extra["redis_connection"]

            url = f"{extra['api_url']}/categories/1/"
            print(url)
            mock_response.get(url, status=200, payload=response_payload)
            result: CategoryModel = await get_category_model_for_answer_callback(callback, extra["api_url"], 1)

    assert isinstance(result, CategoryModel)
    assert result.id == category_init_data["id"]
    assert result.name == category_init_data["name"]
    assert result.url == category_init_data["url"]
    assert result.description == category_init_data["description"]
    assert result.children == category_init_data["children"]
    assert result.products == category_init_data["products"]
    assert result.products == category_init_data["products"]
    assert result.parent_id == category_init_data["parent_id"]

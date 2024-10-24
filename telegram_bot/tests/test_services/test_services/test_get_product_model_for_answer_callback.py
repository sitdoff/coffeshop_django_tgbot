from decimal import Decimal
from unittest.mock import patch

from aiogram.types import CallbackQuery
from aioresponses import aioresponses
from models.models import ProductModel
from services.services import get_product_model_for_answer_callback


async def test_get_product_model_for_answer_callback(callback: CallbackQuery, extra: dict, product_init_data: dict):
    with aioresponses() as mock_response:
        with patch("services.services.get_redis_connection"):
            url = f"{extra['api_url']}/product/1/"
            mock_response.get(url, status=200, payload=product_init_data)
            result: ProductModel = await get_product_model_for_answer_callback(
                callback, extra["redis_connection"], extra["api_url"], 1
            )

    assert isinstance(result, ProductModel)
    assert result.id == product_init_data["product_id"]
    assert result.name == product_init_data["name"]
    assert result.description == product_init_data["description"]
    assert result.category == product_init_data["category"]
    assert result.price == Decimal(product_init_data["price"])
    assert result.quantity == product_init_data["quantity"]
    assert result.parent_id == product_init_data["parent_id"]

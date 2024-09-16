from decimal import Decimal

import pytest
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    URLInputFile,
)
from filters.callback_factories import (
    AddToCartCallbackFactory,
    CategoryCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from lexicon.lexicon_ru import LEXICON_RU
from models.models import ProductModel
from pydantic import ValidationError


@pytest.fixture
def init_data():
    data = {
        "product_id": 1,
        "name": "test_product",
        "description": "test_product_description",
        "category": "test_category",
        "price": "10.00",
        "quantity": 1,
        "parent_id": 1,
        "picture": "http://example.com/image.png",
    }
    yield data


@pytest.fixture
def product(init_data):
    product = ProductModel(**init_data)
    yield product


@pytest.fixture
def product_inline_keyboard(product):
    buttons = [
        [
            InlineKeyboardButton(
                text=LEXICON_RU["inline"]["add_cart"],
                callback_data=AddToCartCallbackFactory(**product.model_dump()).pack(),
            ),
        ],
        [
            InlineKeyboardButton(text="-", callback_data=RemoveFromCartCallbackFactory(**product.model_dump()).pack()),
            InlineKeyboardButton(text="+", callback_data=AddToCartCallbackFactory(**product.model_dump()).pack()),
        ],
        [
            InlineKeyboardButton(
                text=LEXICON_RU["inline"]["back"],
                callback_data=(CategoryCallbackFactory(category_id=product.parent_id).pack()),
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    yield keyboard


def test_product_model_init_with_valid_data(init_data):
    product = ProductModel(**init_data)
    assert product.id == init_data["product_id"]
    assert product.name == init_data["name"]
    assert product.description == init_data["description"]
    assert product.category == init_data["category"]
    assert product.price == init_data["price"]
    assert product.quantity == init_data["quantity"]
    assert product.parent_id == init_data["parent_id"]
    assert product.picture is not None
    assert product.picture.caption == product.name
    assert product.keyboard is not None


def test_product_model_init_with_invalid_data(init_data):
    init_data["product_id"] = str(init_data["product_id"])
    product = ProductModel(**init_data)
    assert product.id == int(init_data["product_id"])

    init_data["price"] = float(init_data["price"])
    with pytest.raises(ValidationError):
        product = ProductModel(**init_data)
    init_data["price"] = "10"

    init_data["quantity"] = str(init_data["quantity"])
    product = ProductModel(**init_data)
    assert product.quantity == int(init_data["quantity"])

    init_data["parent_id"] = str(init_data["parent_id"])
    product = ProductModel(**init_data)
    assert product.parent_id == int(init_data["parent_id"])


def test_product_model_init_if_data_from_redis(init_data):
    del init_data["picture"]
    init_data["is_data_from_redis"] = True

    product = ProductModel(**init_data)
    assert product.id == init_data["product_id"]
    assert product.name == init_data["name"]
    assert product.description == init_data["description"]
    assert product.category == init_data["category"]
    assert product.price == init_data["price"]
    assert product.quantity == init_data["quantity"]
    assert product.parent_id == init_data["parent_id"]
    assert product.picture is None
    assert product.keyboard is None


def test_product_model_cost_property(init_data):
    product = ProductModel(**init_data)
    assert product.cost == str(Decimal(product.price) * product.quantity)

    init_data["quantity"] = 10
    product = ProductModel(**init_data)
    assert product.cost == str(Decimal(product.price) * product.quantity)

    init_data["quantity"] = None
    init_data["is_data_from_redis"] = True
    product = ProductModel(**init_data)
    assert product.cost == str(Decimal(product.price))


def test_product_model_model_dump(init_data):
    init_data["quantity"] = 10
    product = ProductModel(**init_data)
    assert product.model_dump() == {"id": 1, "name": "test_product", "price": "10.00", "quantity": 10, "cost": "100.00"}


def test_product_model_get_product_inline_keyboard(init_data, product_inline_keyboard):
    product = ProductModel(**init_data)
    assert product.get_product_inline_keyboard(init_data) == product_inline_keyboard


def test_product_model_get_picture(init_data):
    product = ProductModel(**init_data)
    picture = product.picture
    assert isinstance(picture, InputMediaPhoto)
    assert picture.caption == init_data["name"]
    assert isinstance(picture.media, URLInputFile)
    assert picture.media.url == init_data["picture"]

    init_data["picture"] = None
    product = ProductModel(**init_data)
    picture = product.picture
    assert isinstance(picture, InputMediaPhoto)
    assert picture.caption == init_data["name"]
    assert isinstance(picture.media, FSInputFile)
    assert picture.media.path == "images/default.jpg"

    init_data["picture"] = "LONG_CACHE_IMAGE_KEY_FROM_TELEGRAM"
    product = ProductModel(**init_data)
    picture = product.picture
    assert isinstance(picture, InputMediaPhoto)
    assert picture.caption == init_data["name"]
    assert picture.media == init_data["picture"]

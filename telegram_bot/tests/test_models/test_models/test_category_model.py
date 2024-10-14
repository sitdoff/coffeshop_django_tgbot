from decimal import Decimal

import pytest
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    URLInputFile,
)
from filters.callback_factories import CategoryCallbackFactory, ProductCallbackFactory
from keyboards.callback_keyboards import set_product_button_text
from lexicon.lexicon_ru import LEXICON_RU
from models.models import CategoryModel, NestedCategoryModel, ProductModel
from pydantic import ValidationError


def test_category_model_init_with_valid_data(category_init_data):
    category = CategoryModel(**category_init_data)
    assert category.id == category_init_data["id"]
    assert category.name == category_init_data["name"]
    assert category.url == category_init_data["url"]
    assert category.description == category_init_data["description"]
    assert category.children == category_init_data["children"]
    assert category.parent == category_init_data["parent"]
    assert category.parent_id == category_init_data["parent_id"]
    assert isinstance(category.picture, InputMediaPhoto)
    assert isinstance(category.picture.media, URLInputFile)
    assert category.picture.caption == category_init_data["name"]
    assert category.keyboard == InlineKeyboardMarkup(inline_keyboard=[])


def test_category_model_init_with_invalid_data(category_init_data):
    category_init_data["id"] = "1"
    category = CategoryModel(**category_init_data)
    category.id = int(category_init_data.get("id"))

    category_init_data["id"] = 1.1
    with pytest.raises(ValidationError):
        category = CategoryModel(**category_init_data)

    category_init_data["id"] = Decimal("1.1")
    with pytest.raises(ValidationError):
        category = CategoryModel(**category_init_data)
    category_init_data["id"] = "1"

    del category_init_data["description"]
    category = CategoryModel(**category_init_data)
    assert category.description == LEXICON_RU["system"]["not_found"]


def test_category_model_method_get_category_inline_keyboard_whith_children(category_init_data):
    category_init_data["children"] = [
        NestedCategoryModel(
            id=1, name="child 1", url="https://example.com/child1", description=None, picture=None
        ).model_dump(),
        NestedCategoryModel(
            id=2, name="child 2", url="https://example.com/child2", description=None, picture=None
        ).model_dump(),
        NestedCategoryModel(
            id=3, name="child 3", url="https://example.com/child3", description=None, picture=None
        ).model_dump(),
    ]
    category = CategoryModel(**category_init_data)
    keyboard = category.keyboard
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == len(category_init_data["children"])
    assert len(keyboard.inline_keyboard[0]) == 1
    assert isinstance(keyboard.inline_keyboard[0][0], InlineKeyboardButton)
    assert isinstance(keyboard.inline_keyboard[1][0], InlineKeyboardButton)
    assert isinstance(keyboard.inline_keyboard[2][0], InlineKeyboardButton)
    for i in range(len(keyboard.inline_keyboard)):
        assert keyboard.inline_keyboard[i][0].text == category_init_data["children"][i]["name"]
        assert (
            keyboard.inline_keyboard[i][0].callback_data
            == CategoryCallbackFactory(category_id=category_init_data["children"][i]["id"]).pack()
        )


def test_category_model_method_get_category_inline_keyboard_whith_products(category_init_data):
    product1_data = {
        "id": 1,
        "name": "test_product",
        "picture": None,
        "description": "test_product_description",
        "category": "http://example.com/category_1",
        "price": "10.00",
        "parent_id": 1,
    }
    product2_data = {
        "id": 2,
        "name": "test_product2",
        "picture": None,
        "description": "test_product2_description",
        "category": "http://example.com/category_2",
        "price": "15.00",
        "parent_id": 1,
    }
    category_init_data["products"] = [product1_data, product2_data]
    category = CategoryModel(**category_init_data)
    keyboard = category.keyboard
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 2
    assert len(keyboard.inline_keyboard[0]) == 1
    assert len(keyboard.inline_keyboard[1]) == 1
    assert isinstance(keyboard.inline_keyboard[0][0], InlineKeyboardButton)
    assert isinstance(keyboard.inline_keyboard[1][0], InlineKeyboardButton)
    assert keyboard.inline_keyboard[0][0].text == set_product_button_text(product1_data)
    assert keyboard.inline_keyboard[0][0].callback_data == ProductCallbackFactory(product_id=product1_data["id"]).pack()
    assert keyboard.inline_keyboard[1][0].text == set_product_button_text(product2_data)
    assert keyboard.inline_keyboard[1][0].callback_data == ProductCallbackFactory(product_id=product2_data["id"]).pack()


def test_category_model_method_get_category_inline_keyboard_whith_parent_id(category_init_data):
    category_init_data["parent_id"] = 1
    category = CategoryModel(**category_init_data)
    keyboard = category.keyboard
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 1
    assert isinstance(keyboard.inline_keyboard[0][0], InlineKeyboardButton)
    assert keyboard.inline_keyboard[0][0].text == LEXICON_RU["inline"]["back"]
    assert (
        keyboard.inline_keyboard[0][0].callback_data
        == CategoryCallbackFactory(category_id=category_init_data["parent_id"]).pack()
    )


def test_category_model_method_get_picture(category_init_data):
    category = CategoryModel(**category_init_data)
    picture = category.picture
    assert isinstance(picture, InputMediaPhoto)
    assert picture.caption == category_init_data["name"]
    assert isinstance(picture.media, URLInputFile)
    assert picture.media.url == category_init_data["picture"]

    category_init_data["picture"] = None
    product = CategoryModel(**category_init_data)
    picture = product.picture
    assert isinstance(picture, InputMediaPhoto)
    assert picture.caption == category_init_data["name"]
    assert isinstance(picture.media, FSInputFile)
    assert picture.media.path == "images/default.jpg"

    category_init_data["picture"] = "LONG_CACHE_IMAGE_KEY_FROM_TELEGRAM"
    product = CategoryModel(**category_init_data)
    picture = product.picture
    assert isinstance(picture, InputMediaPhoto)
    assert picture.caption == category_init_data["name"]
    assert picture.media == category_init_data["picture"]

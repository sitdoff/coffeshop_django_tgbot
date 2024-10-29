from decimal import Decimal

from aiogram.types import FSInputFile, InputMediaPhoto, URLInputFile
from models.models import ProductModel


def test_product_model_init_with_valid_data(product_init_data):
    product = ProductModel(**product_init_data)
    assert product.id == product_init_data["product_id"]
    assert product.name == product_init_data["name"]
    assert product.description == product_init_data["description"]
    assert product.category == product_init_data["category"]
    assert product.price == Decimal(product_init_data["price"])
    assert product.quantity == product_init_data["quantity"]
    assert product.parent_id == product_init_data["parent_id"]
    assert product.picture is not None
    assert product.picture.caption == product.name
    assert product.keyboard is not None


def test_product_model_init_with_invalid_data(product_init_data):
    product_init_data["product_id"] = str(product_init_data["product_id"])
    product = ProductModel(**product_init_data)
    assert product.id == int(product_init_data["product_id"])

    product_init_data["price"] = float(product_init_data["price"])
    product = ProductModel(**product_init_data)

    product_init_data["price"] = Decimal(product_init_data["price"])
    product = ProductModel(**product_init_data)
    product_init_data["price"] = "10"

    product_init_data["quantity"] = str(product_init_data["quantity"])
    product = ProductModel(**product_init_data)
    assert product.quantity == int(product_init_data["quantity"])

    product_init_data["parent_id"] = str(product_init_data["parent_id"])
    product = ProductModel(**product_init_data)
    assert product.parent_id == int(product_init_data["parent_id"])


def test_product_model_init_if_data_from_redis(product_init_data):
    del product_init_data["picture"]
    product_init_data["is_data_from_redis"] = True

    product = ProductModel(**product_init_data)
    assert product.id == product_init_data["product_id"]
    assert product.name == product_init_data["name"]
    assert product.description == product_init_data["description"]
    assert product.category == product_init_data["category"]
    assert product.price == Decimal(product_init_data["price"])
    assert product.quantity == product_init_data["quantity"]
    assert product.parent_id == product_init_data["parent_id"]
    assert product.picture is None
    assert product.keyboard is None


def test_product_model_cost_property(product_init_data):
    product = ProductModel(**product_init_data)
    assert product.cost == product.price * product.quantity

    product_init_data["quantity"] = 10
    product = ProductModel(**product_init_data)
    assert product.cost == product.price * product.quantity

    product_init_data["quantity"] = None
    product_init_data["is_data_from_redis"] = True
    product = ProductModel(**product_init_data)
    assert product.cost == product.price


def test_product_model_model_dump(product_init_data):
    product_init_data["quantity"] = 10
    product = ProductModel(**product_init_data)
    assert product.model_dump() == {
        "id": 1,
        "name": "test_product",
        "price": Decimal("10.00"),
        "quantity": 10,
        "cost": Decimal("100.00"),
    }


def test_product_model_get_product_inline_keyboard(product_init_data, product_inline_keyboard):
    product = ProductModel(**product_init_data)
    assert product.get_product_inline_keyboard(product_init_data) == product_inline_keyboard


def test_product_model_get_picture(product_init_data):
    product = ProductModel(**product_init_data)
    picture = product.picture
    assert isinstance(picture, InputMediaPhoto)
    assert picture.caption == product_init_data["name"]
    assert isinstance(picture.media, URLInputFile)
    assert picture.media.url == product_init_data["picture"]

    product_init_data["picture"] = None
    product = ProductModel(**product_init_data)
    picture = product.picture
    assert isinstance(picture, InputMediaPhoto)
    assert picture.caption == product_init_data["name"]
    assert isinstance(picture.media, FSInputFile)
    assert picture.media.path == "images/default.jpg"

    product_init_data["picture"] = "LONG_CACHE_IMAGE_KEY_FROM_TELEGRAM"
    product = ProductModel(**product_init_data)
    picture = product.picture
    assert isinstance(picture, InputMediaPhoto)
    assert picture.caption == product_init_data["name"]
    assert picture.media == product_init_data["picture"]

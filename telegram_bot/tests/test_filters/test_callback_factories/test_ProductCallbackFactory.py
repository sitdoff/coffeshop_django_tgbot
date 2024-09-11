import pytest
from filters.callback_factories import ProductCallbackFactory
from pydantic import ValidationError


def test_product_callback_factory_with_valid_data():
    factory = ProductCallbackFactory(product_id=1)
    assert factory.product_id == 1
    assert factory.pack() == "product:1"


def test_product_callback_factory_with_product_id_as_string():
    factory = ProductCallbackFactory(product_id="1")
    assert factory.product_id == 1
    assert factory.pack() == "product:1"


def test_product_callback_factory_with_product_id_as_not_string_or_int():
    with pytest.raises(ValidationError):
        ProductCallbackFactory(product_id=[1])
        ProductCallbackFactory(product_id=1.2)
        ProductCallbackFactory(product_id={"product_id": 1})


def test_product_callback_factory_with_product_id_as_invalid_string():
    with pytest.raises(ValidationError):
        ProductCallbackFactory(product_id="1.1")

from decimal import Decimal

import pytest
from filters.callback_factories import AddToCartCallbackFactory
from pydantic import ValidationError


def test_add_to_cart_callback_factory_with_valid_data():
    factory = AddToCartCallbackFactory(id=1, name="test", price="10", quantity=1, cost="10")
    assert factory.id == 1
    assert factory.name == "test"
    assert factory.price == Decimal("10")
    assert factory.quantity == 1
    assert factory.cost == Decimal("10")
    assert factory.pack() == "item:1:test:10:1:10"

    factory = AddToCartCallbackFactory(id="1", name="test", price="10", quantity="1", cost="10")
    assert factory.id == 1
    assert factory.name == "test"
    assert factory.price == Decimal("10")
    assert factory.quantity == 1
    assert factory.cost == Decimal("10")
    assert factory.pack() == "item:1:test:10:1:10"


def test_add_to_cart_callback_factory_with_negative_price():
    with pytest.raises(ValidationError):
        factory = AddToCartCallbackFactory(id=1, name="test", price="-10", quantity=1, cost="10")


def test_add_to_cart_callback_factory_with_negative_quantity():
    with pytest.raises(ValidationError):
        factory = AddToCartCallbackFactory(id=1, name="test", price="10", quantity=-1, cost="10")


def test_add_to_cart_callback_factory_with_negative_cost():
    with pytest.raises(ValidationError):
        factory = AddToCartCallbackFactory(id=1, name="test", price="10", quantity=1, cost="-10")


def test_method_get_product_str_for_redis():
    factory = AddToCartCallbackFactory(id=1, name="test", price="10", quantity=1, cost="10")
    assert factory.get_product_str_for_redis() == "1:test:10:1:10"

    factory = AddToCartCallbackFactory(id="1", name="test", price="10", quantity="1", cost="10")
    assert factory.get_product_str_for_redis() == "1:test:10:1:10"

    factory = AddToCartCallbackFactory(id=1, name="test", price="10", quantity=1, cost="10")
    assert factory.get_product_str_for_redis(template="id_name_price_quantity_cost", separator="_") == "1_test_10_1_10"

    factory = AddToCartCallbackFactory(id="1", name="test", price="10", quantity="1", cost="10")
    assert factory.get_product_str_for_redis(template="id_name_price_quantity_cost", separator="_") == "1_test_10_1_10"


def test_method_unpack_from_redis():
    factory = AddToCartCallbackFactory(id=1, name="test", price="10", quantity=1, cost="10")
    assert AddToCartCallbackFactory.unpack_from_redis(factory.get_product_str_for_redis()) == factory

    factory = AddToCartCallbackFactory(id=1, name="test", price="10", quantity=1, cost="10")
    assert (
        AddToCartCallbackFactory.unpack_from_redis(
            factory.get_product_str_for_redis(template="id_name_price_quantity_cost", separator="_"), separator="_"
        )
        == factory
    )

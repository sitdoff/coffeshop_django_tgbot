from decimal import Decimal

import pytest
from filters.callback_factories import RemoveFromCartCallbackFactory
from pydantic import ValidationError


def test_remove_from_cart_callback_factory_with_valid_data():
    factory = RemoveFromCartCallbackFactory(id=1, name="test", price="100", quantity=10, cost="100")
    assert factory.id == 1
    assert factory.name == "test"
    assert factory.price == Decimal("100")
    assert factory.quantity == 10
    assert factory.cost == Decimal("100")


def test_remove_from_cart_callback_factory_without_quantity():
    factory = RemoveFromCartCallbackFactory(id=1, name="test", price="100", cost="100")
    assert factory.id == 1
    assert factory.name == "test"
    assert factory.price == Decimal("100")
    assert factory.quantity == 1
    assert factory.cost == Decimal("100")


def test_remove_from_cart_callback_factory_with_negative_price():
    with pytest.raises(ValidationError):
        factory = RemoveFromCartCallbackFactory(id=1, name="test", price="-100", quantity=10, cost="100")


def test_remove_from_cart_callback_factory_with_negative_quantity():
    with pytest.raises(ValidationError):
        factory = RemoveFromCartCallbackFactory(id=1, name="test", price="100", quantity=-10, cost="100")


def test_remove_from_cart_callback_factory_with_negative_cost():
    with pytest.raises(ValidationError):
        factory = RemoveFromCartCallbackFactory(id=1, name="test", price="100", quantity=10, cost="-100")

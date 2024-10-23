import pytest
from filters.callback_factories import (
    AddToCartCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from models.cart import Cart


def test_with_add_callback(cart: Cart, add_callbacks: dict[str, AddToCartCallbackFactory]):
    callback = add_callbacks["1"]

    cart._validate_callback_data_and_quantity(callback_data=callback, quantity=1)  # No exception

    with pytest.raises(ValueError) as error:
        cart._validate_callback_data_and_quantity(callback_data=callback, quantity=0)
    assert str(error.value) == "callback_data is AddToCartCallbackFactory, quantity must be positive."

    with pytest.raises(ValueError) as error:
        cart._validate_callback_data_and_quantity(callback_data=callback, quantity=-1)
    assert str(error.value) == "callback_data is AddToCartCallbackFactory, quantity must be positive."


def test_with_remove_callback(cart: Cart, remove_callbacks: dict[str, RemoveFromCartCallbackFactory]):
    callback = remove_callbacks["1"]

    cart._validate_callback_data_and_quantity(callback_data=callback, quantity=-1)  # No exception

    cart._validate_callback_data_and_quantity(callback_data=callback, quantity=0)  # No exception

    with pytest.raises(ValueError) as error:
        cart._validate_callback_data_and_quantity(callback_data=callback, quantity=1)
    assert str(error.value) == "callback_data is RemoveFromCartCallbackFactory, quantity must be negative."

from filters.callback_factories import EditCartCallbackFactory


def test_edit_cart_callback_factory():
    factory = EditCartCallbackFactory()
    assert factory.pack() == "edit_cart:1"

    factory = EditCartCallbackFactory(page=1)
    assert factory.pack() == "edit_cart:1"

    factory = EditCartCallbackFactory(page=100)
    assert factory.pack() == "edit_cart:100"

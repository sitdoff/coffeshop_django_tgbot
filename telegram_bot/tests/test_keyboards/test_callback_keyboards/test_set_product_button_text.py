from keyboards.callback_keyboards import set_product_button_text


def test_set_product_button_text():
    product = {"name": "Кофе", "price": 100}

    result = set_product_button_text(product)
    assert result == "Кофе - 100 руб."

    product = {"name": "Молоко", "price": 50}

    result = set_product_button_text(product)
    assert result == "Молоко - 50 руб."

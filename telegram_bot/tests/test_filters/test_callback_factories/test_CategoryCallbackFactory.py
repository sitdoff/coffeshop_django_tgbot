import pytest
from filters.callback_factories import CategoryCallbackFactory
from pydantic import ValidationError


def test_category_callback_factory_with_valid_data():
    factory = CategoryCallbackFactory(category_id=1, page=1)
    assert factory.category_id == 1
    assert factory.page == 1
    assert factory.pack() == "category:1:1"

    factory = CategoryCallbackFactory(category_id=2, page=2)
    assert factory.category_id == 2
    assert factory.page == 2
    assert factory.pack() == "category:2:2"


def test_category_callback_factory_with_category_id_as_string():
    factory = CategoryCallbackFactory(category_id="1", page=1)
    assert factory.category_id == 1
    assert factory.page == 1
    assert factory.pack() == "category:1:1"

    factory = CategoryCallbackFactory(category_id="2", page=2)
    assert factory.category_id == 2
    assert factory.page == 2
    assert factory.pack() == "category:2:2"


def test_category_callback_factory_with_page_as_string():
    factory = CategoryCallbackFactory(category_id=1, page="1")
    assert factory.category_id == 1
    assert factory.page == 1
    assert factory.pack() == "category:1:1"

    factory = CategoryCallbackFactory(category_id=2, page="2")
    assert factory.category_id == 2
    assert factory.page == 2
    assert factory.pack() == "category:2:2"


def test_category_callback_factory_with_category_id_as_not_string_or_int():
    with pytest.raises(ValidationError):
        CategoryCallbackFactory(category_id=[1], page=1)
        CategoryCallbackFactory(category_id=1.2, page=1)
        CategoryCallbackFactory(category_id={"category_id": 1}, page=1)


def test_category_callback_factory_with_category_id_as_invalid_string():
    with pytest.raises(ValidationError):
        CategoryCallbackFactory(category_id="1.1", page=1)


def test_category_callback_factory_with_page_as_not_string_or_int():
    with pytest.raises(ValidationError):
        CategoryCallbackFactory(category_id=1, page=[1])
        CategoryCallbackFactory(category_id=1, page=1.2)
        CategoryCallbackFactory(category_id=1, page={"page": 1})


def test_category_callback_factory_with_page_as_invalid_string():
    with pytest.raises(ValidationError):
        CategoryCallbackFactory(category_id=1, page="1.1")

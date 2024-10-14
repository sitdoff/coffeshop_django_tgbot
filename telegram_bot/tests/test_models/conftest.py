import pytest
from models.models import CategoryModel


@pytest.fixture
def init_data():
    data = {
        "id": 1,
        "name": "category 1",
        "url": "https://example.com/category1",
        "description": "Category 1 description",
        "children": [],
        "products": [],
        "parent": None,
        "parent_id": None,
        "picture": "http://example.com/category1.jpg",
    }
    yield data


@pytest.fixture
def category(init_data):
    test_category = CategoryModel(**init_data)
    yield test_category

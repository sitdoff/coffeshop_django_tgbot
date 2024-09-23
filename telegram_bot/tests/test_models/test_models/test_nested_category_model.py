import pytest
from aiogram.types import FSInputFile, InputMediaPhoto
from models.models import NestedCategoryModel

# class NestedCategoryModel(BaseModel):
#     """
#     Модель вложенной категории.
#     """
#
#     id: int
#     name: str
#     url: str
#     description: str | None
#     picture: InputMediaPhoto | str | None


@pytest.fixture
def init_data():
    data = {
        "id": 1,
        "name": "test name",
        "url": "http://test.com/test_category",
        "description": "test description",
        "picture": None,
    }
    yield data


def test_nested_category_model_init(init_data):
    model = NestedCategoryModel(**init_data)
    assert model.id == init_data["id"]
    assert model.name == init_data["name"]
    assert model.url == init_data["url"]
    assert model.description == init_data["description"]
    assert model.picture == init_data["picture"]

    init_data["description"] = None
    model = NestedCategoryModel(**init_data)
    assert model.description is None

    init_data["picture"] = "https://test.com/test.jpg"
    model = NestedCategoryModel(**init_data)
    assert model.picture == init_data["picture"]

    init_data["picture"] = InputMediaPhoto(media=FSInputFile("images/default.jpg"), caption=init_data["name"])
    model = NestedCategoryModel(**init_data)
    assert model.picture == init_data["picture"]

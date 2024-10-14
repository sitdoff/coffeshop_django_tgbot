from aiogram.types import FSInputFile, InputMediaPhoto
from models.models import NestedCategoryModel


def test_nested_category_model_init(nested_category_init_data):
    model = NestedCategoryModel(**nested_category_init_data)
    assert model.id == nested_category_init_data["id"]
    assert model.name == nested_category_init_data["name"]
    assert model.url == nested_category_init_data["url"]
    assert model.description == nested_category_init_data["description"]
    assert model.picture == nested_category_init_data["picture"]

    nested_category_init_data["description"] = None
    model = NestedCategoryModel(**nested_category_init_data)
    assert model.description is None

    nested_category_init_data["picture"] = "https://test.com/test.jpg"
    model = NestedCategoryModel(**nested_category_init_data)
    assert model.picture == nested_category_init_data["picture"]

    nested_category_init_data["picture"] = InputMediaPhoto(
        media=FSInputFile("images/default.jpg"), caption=nested_category_init_data["name"]
    )
    model = NestedCategoryModel(**nested_category_init_data)
    assert model.picture == nested_category_init_data["picture"]

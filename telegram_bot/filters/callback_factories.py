from typing import Any

from aiogram.filters.callback_data import CallbackData
from pydantic import field_validator


class CategoryCallbackFactory(CallbackData, prefix="category"):
    category_id: int

    @field_validator("category_id", mode="before")
    def validate_id(cls, value: Any) -> int:
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValueError("id must be an integer or a string representing an integer")
        return value


class ProductCallbackFactory(CallbackData, prefix="product"):
    product_id: int


class AddToCartCallbackFactory(CallbackData, prefix="item"):
    id: int
    name: str
    price: str
    quantity: int
    cost: str

    def get_product_str_for_redis(self, template: str = "id:name:price:quantity:cost") -> str:
        keys = template.split(self.__separator__)
        values = [str(self.model_dump().get(key, "")) for key in keys]
        return self.__separator__.join(values)

    @classmethod
    def unpack_from_redis(cls, value: str):
        value = cls.__prefix__ + cls.__separator__ + value
        return super().unpack(value)


class RemoveFromCartCallbackFactory(CallbackData, prefix="remove"):
    id: int
    name: str
    price: str
    quantity: int = 1
    cost: str

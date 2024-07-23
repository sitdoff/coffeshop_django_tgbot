from typing import Any

from aiogram.filters.callback_data import CallbackData
from pydantic import field_validator


class CategoryCallbackFactory(CallbackData, prefix="category"):
    """
    Фабрика колбэков для категории.
    """

    category_id: int

    @field_validator("category_id", mode="before")
    def validate_id(cls, value: Any) -> int:
        """
        Валидатор поля category_id. Строки переводятся в целые числа.
        Если значение нельзя перевести в целое число, то выбрасывается исключение.
        """
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValueError("category_id must be an integer or a string representing an integer")
        return value


class ProductCallbackFactory(CallbackData, prefix="product"):
    """
    Фабрика колбэков для товаров.
    """

    product_id: int


class AddToCartCallbackFactory(CallbackData, prefix="item"):
    """
    Фабрика колбэков для добавляния товара в корзину.
    """

    id: int
    name: str
    price: str
    quantity: int
    cost: str  # Возможно этот отрибут не нужен. Но пока пусть будет.

    def get_product_str_for_redis(self, template: str = "id:name:price:quantity:cost") -> str:
        """
        Возвращает сроку для корзиные в Redis.
        """
        keys = template.split(self.__separator__)
        values = [str(self.model_dump().get(key, "")) for key in keys]
        return self.__separator__.join(values)

    @classmethod
    def unpack_from_redis(cls, value: str):
        """
        Перобразует сроку из корзины в Redis в экземпляр фабрики.
        """
        value = cls.__prefix__ + cls.__separator__ + value
        return super().unpack(value)


class RemoveFromCartCallbackFactory(CallbackData, prefix="remove"):
    """
    Фабрика колбэков для удаления товара из корзины.
    """

    id: int
    name: str
    price: str
    quantity: int = 1
    cost: str

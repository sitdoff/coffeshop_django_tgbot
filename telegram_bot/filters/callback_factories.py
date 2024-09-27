from typing import Any

from aiogram.filters.callback_data import CallbackData
from pydantic import condecimal, conint, field_validator


class UnpackFromRedisMixin:
    @classmethod
    def unpack_from_redis(cls, value: str, separator: str | None = None) -> CallbackData:
        """
        Перобразует сроку из корзины в Redis в экземпляр фабрики.
        """
        if separator is None:
            separator = cls.__separator__

        value = cls.__prefix__ + cls.__separator__ + cls.__separator__.join(value.split(separator))
        return super().unpack(value)


class CategoryCallbackFactory(CallbackData, prefix="category"):
    """
    Фабрика колбэков для категории.
    """

    category_id: int | str
    page: int | str = 1

    @field_validator("category_id", mode="before")
    def validate_id(cls, value: Any) -> int:
        """
        Валидатор поля "category_id". Строки переводятся в целые числа.
        Если значение нельзя перевести в целое число, то выбрасывается исключение.
        """
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValueError('"category_id" must be an integer or a string representing an integer')
        return value

    @field_validator("page", mode="before")
    def validate_page(cls, value: Any) -> int:
        """
        Валидатор поля "page". Строки переводятся в целые числа.
        Если значение нельзя перевести в целое число, то выбрасывается исключение.
        """
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValueError('"page" must be an integer or a string representing an integer')
        return value


class ProductCallbackFactory(CallbackData, prefix="product"):
    """
    Фабрика колбэков для товаров.
    """

    product_id: int

    @field_validator("product_id", mode="before")
    def validate_page(cls, value: Any) -> int:
        """
        Валидатор поля "product_id". Строки переводятся в целые числа.
        Если значение нельзя перевести в целое число, то выбрасывается исключение.
        """
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValueError('"product_id" must be an integer or a string representing an integer')
        return value


class AddToCartCallbackFactory(UnpackFromRedisMixin, CallbackData, prefix="item"):
    """
    Фабрика колбэков для добавляния товара в корзину.
    """

    id: int
    name: str
    price: condecimal(ge=0, max_digits=10, decimal_places=2)
    quantity: conint(ge=1)
    cost: condecimal(ge=0, max_digits=10, decimal_places=2)  # Возможно этот отрибут не нужен. Но пока пусть будет.

    def get_product_str_for_redis(
        self, template: str = "id:name:price:quantity:cost", separator: str | None = None
    ) -> str:
        """
        Возвращает сроку для корзиные в Redis.
        """
        if separator is None:
            separator = self.__separator__

        keys = template.split(separator)
        values = [str(self.model_dump().get(key, "")) for key in keys]
        return separator.join(values)


class RemoveFromCartCallbackFactory(UnpackFromRedisMixin, CallbackData, prefix="remove"):
    """
    Фабрика колбэков для удаления товара из корзины.
    """

    id: int
    name: str
    price: condecimal(ge=0, max_digits=10, decimal_places=2)
    quantity: conint(ge=0) = 1
    cost: condecimal(ge=0, max_digits=10, decimal_places=2)


class EditCartCallbackFactory(CallbackData, prefix="edit_cart"):
    """
    Фабрика колбэков для редактирования корзины.
    """

    page: int = 1

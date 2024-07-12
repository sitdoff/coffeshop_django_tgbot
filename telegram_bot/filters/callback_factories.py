from aiogram.filters.callback_data import CallbackData


class CategoryCallbackFactory(CallbackData, prefix="category"):
    category_id: int


class ProductCallbackFactory(CallbackData, prefix="product"):
    product_id: int


class AddToCartCallbackFactory(CallbackData, prefix="add_to_cart"):
    id: int
    name: str
    price: str
    quantity: int
    cost: str

    def get_product_str_for_redis(self, template: str = "id:name:price:quantity:cost") -> str:
        keys = template.split(self.__separator__)
        values = [str(self.model_dump().get(key, "")) for key in keys]
        return self.__separator__.join(values)

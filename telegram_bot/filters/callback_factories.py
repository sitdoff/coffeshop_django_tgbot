from aiogram.filters.callback_data import CallbackData


class CategoryCallbackFactory(CallbackData, prefix="category"):
    category_id: int


class ProductCallbackFactory(CallbackData, prefix="product"):
    product_id: int

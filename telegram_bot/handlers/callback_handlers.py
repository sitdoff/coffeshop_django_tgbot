import logging
from typing import Any, Literal

from aiogram import F, Router
from aiogram.types import CallbackQuery
from filters.callback_factories import (
    AddToCartCallbackFactory,
    CategoryCallbackFactory,
    ProductCallbackFactory,
)
from lexicon.lexicon_ru import LEXICON_RU
from services import cart_services, services

logger = logging.getLogger(__name__)

router: Router = Router()


@router.callback_query(F.data == "make_order")
@router.callback_query(CategoryCallbackFactory.filter())
async def process_category_callback(
    callback: CallbackQuery,
    extra: dict[Literal["redis_connection", "api_url"], Any],
    callback_data: CategoryCallbackFactory | None = None,
):
    category_id = callback_data.category_id if callback_data else None
    logger.debug("Callback data: %s", callback_data)

    category = await services.get_category_model_for_answer_callback(
        callback, extra["redis_connection"], extra["api_url"], category_id
    )

    await callback.message.edit_media(
        media=category.picture,
        reply_markup=category.keyboard,
    )


@router.callback_query(ProductCallbackFactory.filter())
async def process_product_callback(
    callback: CallbackQuery,
    extra: dict[Literal["redis_connection", "api_url"], Any],
    callback_data: ProductCallbackFactory,
):
    logger.debug("Product callback data: %s", callback_data.pack())

    product = await services.get_product_model_for_answer_callback(
        callback, extra["redis_connection"], extra["api_url"], callback_data.product_id
    )
    logger.debug("Data for answer: %s", product)

    await callback.message.edit_media(
        media=product.picture,
        reply_markup=product.keyboard,
    )


@router.callback_query(F.data == "pass")
async def process_pass_callback(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU["system"]["wip"], show_alert=True)


@router.callback_query(AddToCartCallbackFactory.filter())
async def add_to_cart(callback: CallbackQuery, callback_data: AddToCartCallbackFactory, extra: dict[str, Any]):
    redis_cart_manager = cart_services.CartManager(
        redis_connection=extra["redis_connection"], user_id=callback.from_user.id
    )
    await redis_cart_manager.add_product_in_redis_cart(callback_data=callback_data)
    print(await redis_cart_manager.get_cart_info())
    await callback.answer(text=LEXICON_RU["inline"]["added"])

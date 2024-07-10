import logging
from typing import Any, Literal

from aiogram import F, Router
from aiogram.types import CallbackQuery
from keyboards.callback_keyboards import CategoryCallbackFactory, ProductCallbackFactory
from services.services import (
    get_data_for_answer_category_callback,
    get_data_for_answer_product_callback,
)

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

    data_for_answer = await get_data_for_answer_category_callback(
        callback, extra["redis_connection"], extra["api_url"], category_id
    )

    await callback.message.edit_media(
        media=data_for_answer["picture"],
    )
    await callback.message.edit_caption(
        caption=data_for_answer["description"],
        reply_markup=data_for_answer["keyboard"],
    )


@router.callback_query(ProductCallbackFactory.filter())
async def process_product_callback(
    callback: CallbackQuery,
    extra: dict[Literal["redis_connection", "api_url"], Any],
    callback_data: ProductCallbackFactory,
):
    logger.debug("Product callback data: %s", callback_data)

    data_for_answer = await get_data_for_answer_product_callback(
        callback, extra["redis_connection"], extra["api_url"], callback_data.product_id
    )
    logger.debug("Data for answer: %s", data_for_answer)

    await callback.message.edit_media(
        media=data_for_answer["picture"],
    )
    await callback.message.edit_caption(
        caption=data_for_answer["description"],
        reply_markup=data_for_answer["keyboard"],
    )

import logging
from typing import Any, Literal

import redis
from aiogram import F, Router
from aiogram.types import CallbackQuery
from keyboards.callback_keyboards import CategoryCallbackFactory
from services.services import get_data_for_answer_category_callback

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

    category_description, picture, keyboard = await get_data_for_answer_category_callback(
        callback, extra["redis_connection"], extra["api_url"], category_id
    )

    await callback.message.edit_media(
        media=picture,
    )
    await callback.message.edit_caption(
        caption=category_description,
        reply_markup=keyboard,
    )

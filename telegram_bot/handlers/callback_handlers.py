import redis
from aiogram import F, Router
from aiogram.types import CallbackQuery
from filters.callback_filters import IsCategoryCallback
from services.services import get_data_for_answer_category_callback

router: Router = Router()


@router.callback_query(F.data == "make_order")
@router.callback_query(IsCategoryCallback("category"))
async def process_category_callback(
    callback: CallbackQuery,
    redis_connection: redis.Redis,
    api_url: str,
    category_id: str = None,
):
    category_description, keyboard = await get_data_for_answer_category_callback(
        callback, redis_connection, api_url, category_id
    )
    await callback.message.edit_text(
        text=category_description,
        reply_markup=keyboard,
    )

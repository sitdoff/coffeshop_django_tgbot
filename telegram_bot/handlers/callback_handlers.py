import logging
from typing import Any, Literal

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from filters.callback_factories import (
    AddToCartCallbackFactory,
    CategoryCallbackFactory,
    ProductCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from lexicon.lexicon_ru import LEXICON_RU
from models.cart import Cart
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

    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    keyboard = product.keyboard
    keyboard = await cart.edit_product_inline_keyboard(keyboard_list=keyboard.inline_keyboard)

    await callback.message.edit_media(
        media=product.picture,
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "pass")
async def process_pass_callback(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU["system"]["wip"], show_alert=True)


@router.callback_query(AddToCartCallbackFactory.filter())
async def add_to_cart(callback: CallbackQuery, callback_data: AddToCartCallbackFactory, extra: dict[str, Any]):
    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    await cart.add_product_in_cart(callback_data)
    keyboard = await cart.edit_product_inline_keyboard(callback.message.reply_markup.inline_keyboard)
    if callback.message.reply_markup != keyboard:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer(text=LEXICON_RU["inline"]["added"])


@router.callback_query(RemoveFromCartCallbackFactory.filter())
async def remove_from_cart(
    callback: CallbackQuery, callback_data: RemoveFromCartCallbackFactory, extra: dict[str, Any]
):
    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    await cart.get_items_from_redis()
    if str(callback_data.id) not in cart.items or cart.items[str(callback_data.id)].quantity <= 0:
        await callback.answer(text=LEXICON_RU["inline"]["item_is_not_in_cart"])
    else:
        await cart.remove_product_from_cart(callback_data)
        keyboard = await cart.edit_product_inline_keyboard(callback.message.reply_markup.inline_keyboard)
        if callback.message.reply_markup != keyboard:
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer(text=LEXICON_RU["inline"]["removed"])

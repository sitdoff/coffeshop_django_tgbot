import logging
from typing import Any, Literal

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from filters.callback_factories import (
    AddToCartCallbackFactory,
    CategoryCallbackFactory,
    EditCartCallbackFactory,
    ProductCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from lexicon.lexicon_ru import LEXICON_RU
from models.cart import Cart
from services import services

logger = logging.getLogger(__name__)

router: Router = Router()


@router.callback_query(F.data == "make_order")
@router.callback_query(CategoryCallbackFactory.filter())
async def process_category_callback(
    callback: CallbackQuery,
    extra: dict[Literal["redis_connection", "api_url"], Any],
    callback_data: CategoryCallbackFactory | None = None,
):
    """
    Хэндлер для обработки колбэков кнопок категорий.
    """
    category_id = callback_data.category_id if callback_data else None
    logger.debug("Callback data: %s", callback_data)

    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)

    category = await services.get_category_model_for_answer_callback(
        callback, extra["redis_connection"], extra["api_url"], category_id
    )
    paginated_keyboard = services.pagination_keyboard(
        keyboard=category.keyboard,
        page=callback_data.page if callback_data else 1,
        category_id=category_id,
        factory=CategoryCallbackFactory,
    )
    keyboard_with_cart_button = await cart.edit_category_inline_keyboard(
        keyboard_list=paginated_keyboard.inline_keyboard
    )

    if category_id is None:
        await callback.message.edit_media(
            media=category.picture,
            reply_markup=keyboard_with_cart_button,
        )
    else:
        await callback.message.edit_media(
            media=category.picture,
            reply_markup=keyboard_with_cart_button,
        )


@router.callback_query(ProductCallbackFactory.filter())
async def process_product_callback(
    callback: CallbackQuery,
    extra: dict[Literal["redis_connection", "api_url"], Any],
    callback_data: ProductCallbackFactory,
):
    """
    Хэндлер для обработки колбэков кнопок товаров.
    """
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
    """
    Хэндлер для обработки колбэков с кнопок, которые еще не готовы.
    """
    logger.debug("Callback data: %s", callback.data)
    await callback.answer(text=LEXICON_RU["system"]["wip"], show_alert=True)


@router.callback_query(AddToCartCallbackFactory.filter())
async def add_to_cart(callback: CallbackQuery, callback_data: AddToCartCallbackFactory, extra: dict[str, Any]):
    """
    Хэндлер для обработки колбэков кнопок добавления товара в корзину.
    """
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
    """
    Хэндлер обработки колбэков с кнопок удаления товара из корзины.
    """
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


@router.callback_query(F.data == "cart")
async def process_cart_callback(callback: CallbackQuery, extra: dict[str, Any]):
    """
    Хэндлер для обработки колбэков кнопоки корзины.
    """
    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    keyboard = cart.get_cart_inline_keyboard()
    await cart.get_items_from_redis()
    await callback.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile("images/cart.jpg"), caption=cart.get_cart_text()), reply_markup=keyboard
    )


@router.callback_query(EditCartCallbackFactory.filter())
async def process_edit_cart_callback(
    callback: CallbackQuery, extra: dict[str, Any], callback_data: EditCartCallbackFactory
):
    """
    Хэндлер для обработки колбэков кнопоки редактирования корзины.
    """
    logger.debug("Edit cart callback data: %s", callback_data)
    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    await cart.get_items_from_redis()
    keyboard = await cart.get_edit_cart_inline_keyboard()
    await callback.message.edit_reply_markup(
        reply_markup=services.pagination_keyboard(
            keyboard=keyboard,
            page=callback_data.page,
            category_id=None,
            factory=EditCartCallbackFactory,
        )
    )

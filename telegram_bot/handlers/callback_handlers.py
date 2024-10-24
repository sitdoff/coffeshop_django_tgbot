import logging
from typing import Any, Literal

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from filters.callback_factories import (
    AddToCartCallbackFactory,
    CategoryCallbackFactory,
    EditCartCallbackFactory,
    ProductCallbackFactory,
    RemoveFromCartCallbackFactory,
)
from keyboards.callback_keyboards import get_start_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from models.cart import Cart
from services import cache_services, services

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
    logger.info("Handler for category")
    category_id = callback_data.category_id if callback_data else None
    logger.info("Callback: %s", callback.data)
    logger.info("Callback data: %s", callback_data)

    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)

    category = await services.get_category_model_for_answer_callback(callback, extra["api_url"], category_id)
    paginated_keyboard = services.pagination_keyboard(
        keyboard=category.keyboard,
        page=callback_data.page if callback_data else 1,
        category_id=category_id,
        factory=CategoryCallbackFactory,
    )
    keyboard_with_cart_button = await services.edit_category_inline_keyboard(
        cart=cart, keyboard_list=paginated_keyboard.inline_keyboard
    )
    event = await callback.message.edit_media(
        media=category.picture,
        reply_markup=keyboard_with_cart_button,
    )
    await cache_services.save_photo_file_id(event, extra["redis_connection"])


@router.callback_query(ProductCallbackFactory.filter())
async def process_product_callback(
    callback: CallbackQuery,
    extra: dict[Literal["redis_connection", "api_url"], Any],
    callback_data: ProductCallbackFactory,
):
    """
    Хэндлер для обработки колбэков кнопок товаров.
    """
    logger.info("Handler for product")
    logger.info("Callback: %s", callback.data)
    logger.info("Product callback data: %s", callback_data)

    product = await services.get_product_model_for_answer_callback(callback, extra["api_url"], callback_data.product_id)
    logger.debug("Data for answer: %s", product)

    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    keyboard = product.keyboard
    keyboard = await services.edit_product_inline_keyboard(cart, keyboard_list=keyboard.inline_keyboard)

    answer = await callback.message.edit_media(
        media=product.picture,
        reply_markup=keyboard,
    )
    await cache_services.save_photo_file_id(answer, extra["redis_connection"])


@router.callback_query(F.data == "pass")
async def process_pass_callback(callback: CallbackQuery):
    """
    Хэндлер для обработки колбэков с кнопок, которые еще не готовы.
    """
    logger.info("Handler for pass")
    logger.info("Callback: %s", callback.data)
    await callback.answer(text=LEXICON_RU["system"]["wip"], show_alert=True)


@router.callback_query(AddToCartCallbackFactory.filter())
async def add_to_cart(callback: CallbackQuery, callback_data: AddToCartCallbackFactory, extra: dict[str, Any]):
    """
    Хэндлер для обработки колбэков кнопок добавления товара в корзину.
    """
    logger.info("Handler for add cart")
    logger.info("Callback: %s", callback.data)
    logger.info("Callback data: %s", callback_data)
    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    await cart.add_product_in_cart(callback_data)
    keyboard = await services.edit_product_inline_keyboard(cart, callback.message.reply_markup.inline_keyboard)
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
    logger.info("Handler for remove from cart")
    logger.info("Callback: %s", callback.data)
    logger.info("Callback data: %s", callback_data)
    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    await cart.get_items_from_redis()
    if str(callback_data.id) not in cart.items or cart.items[str(callback_data.id)].quantity <= 0:
        await callback.answer(text=LEXICON_RU["inline"]["item_is_not_in_cart"])
    else:
        await cart.remove_product_from_cart(callback_data)
        keyboard = await services.edit_product_inline_keyboard(cart, callback.message.reply_markup.inline_keyboard)
        if callback.message.reply_markup != keyboard:
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer(text=LEXICON_RU["inline"]["removed"])


@router.callback_query(F.data == "cart")
async def process_cart_callback(callback: CallbackQuery, extra: dict[str, Any]):
    """
    Хэндлер для обработки колбэков кнопоки корзины.
    """
    logger.info("Handler for cart button")
    logger.info("Callback: %s", callback.data)

    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    keyboard = cart.get_cart_inline_keyboard()
    await cart.get_items_from_redis()
    caption = cart.get_cart_text()
    photo = await cache_services.get_photo_file_id("cart", extra["redis_connection"]) or InputMediaPhoto(
        media=FSInputFile("images/cart.jpg")
    )
    photo.caption = caption
    answer = await callback.message.edit_media(media=photo, reply_markup=keyboard)
    await cache_services.save_photo_file_id(answer, extra["redis_connection"], key="cart")


@router.callback_query(EditCartCallbackFactory.filter())
async def process_edit_cart_callback(
    callback: CallbackQuery, extra: dict[str, Any], callback_data: EditCartCallbackFactory
):
    """
    Хэндлер для обработки колбэков кнопоки редактирования корзины.
    """
    logger.info("Handler for edit cart")
    logger.info("Callback: %s", callback.data)
    logger.info("Callback data: %s", callback_data)
    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    await cart.get_items_from_redis()
    keyboard = await services.get_edit_cart_inline_keyboard(cart)
    await callback.message.edit_reply_markup(
        reply_markup=services.pagination_keyboard(
            keyboard=keyboard,
            page=callback_data.page,
            category_id=None,
            factory=EditCartCallbackFactory,
        )
    )


@router.callback_query(F.data == "clear_cart")
async def process_cart_clear_callback(callback: CallbackQuery, extra: dict[str, Any]):
    """
    Хэндлер для обработки колбэка очистки корзины
    """
    logger.info("Handler for clear cart")
    logger.info("Callback: %s", callback.data)
    cart = Cart(redis_connection=extra["redis_connection"], user_id=callback.from_user.id)
    photo = await cache_services.get_photo_file_id("clear_cart", extra["redis_connection"]) or FSInputFile(
        "images/cart.jpg"
    )
    photo.caption = LEXICON_RU["messages"]["cart_is_empty"]
    await cart.clear()
    answer = await callback.message.edit_media(
        media=(
            InputMediaPhoto(media=photo, caption=LEXICON_RU["messages"]["cart_is_empty"])
            if isinstance(photo, FSInputFile)
            else photo
        ),
        reply_markup=await get_start_keyboard(),
    )
    await cache_services.save_photo_file_id(answer, extra["redis_connection"], key="clear_cart")

from string import Template
from typing import Any, Literal

LEXICON_RU: dict[Literal["system", "commands", "inline", "messages"], Any] = {
    "system": {
        "config_loaded": "Configuration loaded.",
        "bot_created": "Bot created.",
        "dispatcher_created": "Dispatcher created.",
        "bot_config_loaded": "Bot config loaded.",
        "api_config_loaded": "API config loaded.",
        "redis_config_loaded": "Redis config loaded.",
        "redis_connection_created": "Redis connection created.",
        "workflow_data_updated": "Workflow data updated.",
        "main_menu_set": "Main menu installed.",
        "routers_registred": "Routers registred.",
        "wrong": "Something went wrong. ❌",
        "wip": "Work in progress. 🚧",
        "not_found": "Не найдено",
    },
    "commands": {
        "start": r"Приветствуем вас в нашей кофейне\.\n\nХотите сделать заказ, который будет готов к вашему приходу?",
        "help": "Help.",
    },
    "inline": {
        "make_order": "Сделать заказ",
        "add_to_order": "Дополнить заказ",
        "my_orders": "Мои заказы",
        "back": "< Назад",
        "cart": Template("🛒 Корзина($total_cost руб.)"),
        "add_cart": "Добавить 1 шт в корзину ➕",
        "product_quantity_in_cart": Template("в корзине $count шт."),
        "added": "Товар добавлен в корзину.",
        "removed": "Товар удален из корзины.",
        "item_is_not_in_cart": "Товара нет в корзине.",
        "edit_cart": "Редактировать корзину",
        "checkout": "Оформить заказ",
    },
    "messages": {
        "cart_info": "Итог",
        "rub_symbol": "₽",
        "cart_text_head": "Товары в вашей корзине",
    },
}

LEXICON_MAIN_MENU_RU = {
    "/start": "Start",
    "/help": "Help",
    "/cart": "Cart",
}

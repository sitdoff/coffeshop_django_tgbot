from typing import Any, Literal

LEXICON_RU: dict[Literal["system", "commands", "inline"], Any] = {
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
    },
    "commands": {
        "start": "Приветствуем вас в нашей кофейне.\n\nХотите сделать заказ, который будет готов к вашему приходу?",
        "help": "Help.",
    },
    "inline": {
        "make_order": "Сделать заказ",
        "my_orders": "Мои заказы",
        "back": "< Назад",
        "add_cart": "Добавить в корзину",
    },
}

LEXICON_MAIN_MENU_RU = {
    "/start": "Start",
    "/help": "Help",
}

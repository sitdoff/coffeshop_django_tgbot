from typing import Any, Literal

LEXICON_RU: dict[Literal["system", "commands"], Any] = {
    "system": {
        "config_loaded": "Configuration loaded.",
        "bot_created": "Bot created.",
        "dispatcher_created": "Dispatcher created.",
        "bot_config_loaded": "Bot config loaded.",
        "redis_config_loaded": "Redis config loaded.",
        "redis_connection_created": "Redis connection created.",
        "workflow_data_updated": "Workflow data updated.",
        "routers_registred": "Routers registred.",
        "wrong": "Something went wrong.",
    },
    "commands": {
        "start": "Start.",
        "help": "Help.",
    },
}

from tortoise import Tortoise

DB_PATH = "core/vivaldi_bot.db"  # или просто "bot.db" в корне проекта


TORTOISE_ORM = {
    "connections": {
        "default": f"sqlite://{DB_PATH}",
    },
    "apps": {
        "models": {
            "models": ["core.models", "aerich.models"],  # aerich — если захочешь миграции
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Инициализация подключения Tortoise ORM."""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close_db():
    """Закрытие подключения."""
    await Tortoise.close_connections()
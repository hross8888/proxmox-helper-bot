from tortoise import Tortoise

from core.models import Setting
from core.redis import redis_client

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

async def get_banner_file_id():
    banner_file_id = await redis_client.get("banner_file_id")
    if banner_file_id:
        return banner_file_id

    setting = await Setting.all().first()
    if setting and setting.banner_file_id:
        await redis_client.set("banner_file_id", setting.banner_file_id)
        return setting.banner_file_id

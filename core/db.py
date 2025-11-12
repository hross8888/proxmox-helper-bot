from tortoise import Tortoise

from core.models import Setting, Vm
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
    """Инициализация подключения БД"""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close_db():
    """Закрытие подключения"""
    await Tortoise.close_connections()

async def get_banner_file_id():
    banner_file_id = await redis_client.get("banner_file_id")
    if banner_file_id:
        return banner_file_id

    setting = await Setting.all().first()
    if setting and setting.banner_file_id:
        await redis_client.set("banner_file_id", setting.banner_file_id)
        return setting.banner_file_id

async def set_banner_file_id(file_id):
    """Установить set_banner_file_id баннера"""
    setting = await Setting.all().first()
    if not setting:
        await Setting.create(banner_file_id=file_id)
    else:
        setting.banner_file_id = file_id
        await setting.save(update_fields=["banner_file_id"])
    await redis_client.set("banner_file_id", setting.banner_file_id)


async def set_db(data: list[dict]):
    """Полностью перезаписать таблицу Vm"""
    await Vm.all().delete()
    if data:
        await Vm.bulk_create([Vm(**item) for item in data])
    return len(data)

async def merge_db(data: list[dict]):
    """Добавить новые записи."""
    existing = {v["vm_id"] for v in await Vm.all().values("vm_id")}
    new_items = [Vm(**item) for item in data if item["vm_id"] not in existing]
    if new_items:
        await Vm.bulk_create(new_items)
    return len(new_items)
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from common.types import Language, DEFAULT_LANGUAGE

from bot.i18n.i18n import I18n
from core.settings import BOT_TOKEN, REDIS_URL

BOT = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = RedisStorage.from_url(REDIS_URL)
DP = Dispatcher(storage=storage)


i18n_path = Path(__file__).resolve().parent.joinpath('i18n')
i18n_all = {
    Language.RU: I18n(i18n_path.joinpath('ru.yaml')),
}
i18n_default = i18n_all[DEFAULT_LANGUAGE]

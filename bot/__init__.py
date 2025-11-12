from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from common.types import Language, DEFAULT_LANGUAGE

from bot.i18n.i18n import I18n
from core.settings import BOT_TOKEN

BOT = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
DP = Dispatcher(storage=storage)


i18n_path = Path(__file__).resolve().parent.joinpath('i18n')
i18n_all = {
    Language.RU: I18n(i18n_path.joinpath('ru.yaml')),
}
i18n_default = i18n_all[DEFAULT_LANGUAGE]

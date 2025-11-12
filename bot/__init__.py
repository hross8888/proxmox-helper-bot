from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

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


async def setup_bot_commands():
    await BOT.set_my_commands(
        [
            BotCommand(command="start", description=i18n_default("CMD.RESTART")),
            BotCommand(command="set_db", description=i18n_default("CMD.SET_DB")),
            BotCommand(command="get_db", description=i18n_default("CMD.GET_DB")),
            BotCommand(command="merge_db", description=i18n_default("CMD.MERGE_DB")),
        ],
        scope=BotCommandScopeDefault()
    )
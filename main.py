import asyncio
import contextlib

from aiogram import F
from aiogram.types import BotCommand, BotCommandScopeDefault, CallbackQuery
from loguru import logger

from bot import BOT, DP
from bot.middleware.check_user import CheckUser
from bot.middleware.error import ErrorMiddleware
from bot.middleware.logger import LoggingMiddleware
from core.db import init_db, close_db
from services.pve import proxmox
from utils.logger import setup_logger

from bot.bot_loader import register_all_handlers


async def on_startup():
    # setup_logger()
    await init_db()
    # await Vm.all().delete()
    register_all_handlers(DP)
    DP.update.outer_middleware(CheckUser())
    DP.update.outer_middleware(LoggingMiddleware())
    DP.update.outer_middleware(ErrorMiddleware())

    logger.info("Bot started")


async def on_shutdown():
    with contextlib.suppress(Exception):
        await close_db()
        await proxmox.close()

async def setup_bot_commands():
    await BOT.set_my_commands(
        [
            BotCommand(command="start", description="Перезапустить бота"),
        ],
        scope=BotCommandScopeDefault()
    )

async def main():
    logger.info("Запуск Telegram-бота для управления Proxmox...")
    DP.startup.register(on_startup)
    DP.shutdown.register(on_shutdown)



    try:
        await setup_bot_commands()
        await DP.start_polling(BOT)
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Бот остановлен пользователем.")
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
    finally:
        with contextlib.suppress(Exception):
            await BOT.session.close()
        logger.info("Бот завершил работу.")


if __name__ == "__main__":
    asyncio.run(main())

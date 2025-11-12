from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from loguru import logger

from core.settings import ADMIN_IDS


class CheckUser(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        tg_user_id = data["event_from_user"].id

        if tg_user_id not in ADMIN_IDS:
            logger.info(f"Bad user: {tg_user_id}")
            return

        message = event.callback_query.message if event.callback_query else event.message
        if message.chat.type != "private":
            return


        return await handler(event, data)

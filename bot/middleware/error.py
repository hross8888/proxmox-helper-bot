from aiogram import BaseMiddleware
from aiogram.types import LinkPreviewOptions

from loguru import logger

from bot import i18n_default


class ErrorMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        msg = getattr(getattr(event, "callback_query", None), "message", None) or getattr(event, "message", None)
        user = (
                getattr(event, "from_user", None)
                or getattr(getattr(event, "message", None), "from_user", None)
                or getattr(getattr(event, "callback_query", None), "from_user", None)
        )

        user_id = getattr(user, "id", None)

        try:
            return await handler(event, data)

        except Exception as e:
            logger.exception(f"Необработанное исключение у юзера {user_id}: {e}")
            text = i18n_default("M.PVE.ERROR.LOGGER_MIDDLEWARE").format(exc=e)
            await msg.answer(text, parse_mode="html", link_preview_options=LinkPreviewOptions(is_disabled=True))



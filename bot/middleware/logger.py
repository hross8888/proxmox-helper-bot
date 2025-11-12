from aiogram import BaseMiddleware
from loguru import logger
from typing import Callable, Dict, Any, Awaitable


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ):
        user = (
            getattr(event, "from_user", None)
            or getattr(getattr(event, "message", None), "from_user", None)
            or getattr(getattr(event, "callback_query", None), "from_user", None)
        )
        user_id = getattr(user, "id", None)

        text = None
        if getattr(event, "message", None):
            text = getattr(event.message, "text", None)
        elif getattr(event, "callback_query", None):
            text = getattr(event.callback_query, "data", None)
        elif getattr(event, "text", None):  # На случай обычного Message
            text = event.text


        state = data.get("state")
        if state:
            current_state = await state.get_state()
            current_data = await state.get_data()
        else:
            current_state = None
            current_data = None

        logger.info(
            f"User: {user_id} | Data: {text} | State: {current_state} | Data: {current_data}"
        )

        return await handler(event, data)

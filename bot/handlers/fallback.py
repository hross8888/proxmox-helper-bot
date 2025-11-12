from aiogram import Router, F
from aiogram.types import CallbackQuery
from loguru import logger

router = Router(name=__name__)


@router.callback_query(F.data)
async def fallback_callback(query: CallbackQuery):
    await query.answer("Not Implemented", show_alert=True)
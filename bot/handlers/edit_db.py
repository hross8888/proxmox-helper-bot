import json

from bot import i18n_default
from bot.edit_db.states import DbStates
from core.db import set_db, merge_db

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router(name=__name__)


@router.message(DbStates.waiting_for_set_json)
async def process_set_db_json(message: Message, state: FSMContext):
    try:
        data = json.loads(message.text)
        count = await set_db(data)
        await message.answer(i18n_default("M.DB.SET_DB_RESULT").format(count=count))
    except json.JSONDecodeError:
        await message.answer(i18n_default("M.DB.ERROR.JSON"))
        return
    await state.clear()


@router.message(DbStates.waiting_for_merge_json)
async def process_merge_db_json(message: Message, state: FSMContext):
    try:
        data = json.loads(message.text)
        added = await merge_db(data)
        await message.answer(i18n_default("M.DB.MERGE_DB_RESULT").format(count=added))
    except json.JSONDecodeError:
        await message.answer(i18n_default("M.DB.ERROR.JSON"))
        return
    await state.clear()

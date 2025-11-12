import json

from aiogram.exceptions import TelegramBadRequest

from bot import i18n_default
from bot.edit_db.states import DbStates
from bot.keyboards.common_kbs import close_kb
from bot.utils.message_helper import delete_messages, temporary_message
from core.db import set_db, merge_db

from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router(name=__name__)


@router.message(DbStates.waiting_for_set_json)
async def process_set_db_json(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    delete_msg_id = data.get("delete_msg_id")
    if delete_msg_id:
        try:
            await bot.delete_message(message.chat.id, delete_msg_id)
        except TelegramBadRequest:
            pass

    try:
        data = json.loads(message.text)
        count = await set_db(data)
        await temporary_message(message=message, text=i18n_default("M.DB.SET_DB_RESULT").format(count=count))
    except json.JSONDecodeError:
        await message.answer(i18n_default("M.DB.ERROR.JSON"), reply_markup=close_kb())
        return
    await state.clear()


@router.message(DbStates.waiting_for_merge_json)
async def process_merge_db_json(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    delete_msg_id = data.get("delete_msg_id")
    if delete_msg_id:
        try:
            await bot.delete_message(message.chat.id, delete_msg_id)
        except TelegramBadRequest:
            pass
    try:
        data = json.loads(message.text)
        added = await merge_db(data)
        await temporary_message(message=message, text=i18n_default("M.DB.MERGE_DB_RESULT").format(count=added))
    except json.JSONDecodeError:
        await message.answer(i18n_default("M.DB.ERROR.JSON"), reply_markup=close_kb())
        return
    await state.clear()

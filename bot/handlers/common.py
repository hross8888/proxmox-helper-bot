from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.callbacks import CloseCallback
from bot.keyboards.proxmox_kbs import BackCallback
from bot.pve.flow import next_step, render_step, prev_step

router = Router(name=__name__)


async def handle_step(query: CallbackQuery, state: FSMContext, is_next: bool = True):
    await query.answer()
    await (next_step(state) if is_next else prev_step(state))
    await render_step(query, state)


@router.callback_query(BackCallback.filter())
async def back_kb_handler(query: CallbackQuery, state: FSMContext):
    await handle_step(query, state, is_next=False)

@router.callback_query(CloseCallback.filter())
async def back_kb_handler(query: CallbackQuery, state: FSMContext):
    try:
        await query.message.delete()
    except TelegramBadRequest:
        pass

@router.message(F.content_type.in_({"photo"}))
async def show_file_id(message: Message):
    file_id = message.photo[-1].file_id if message.photo else None
    if file_id:
        await message.answer(f"file_id: <code>{file_id}</code>")

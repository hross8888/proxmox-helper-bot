import html
import json
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from bot import i18n_default
from bot.edit_db.states import DbStates
from bot.keyboards.proxmox_kbs import main_proxmox_kb
from core.db import get_banner_file_id, set_banner_file_id, set_db, merge_db
from core.models import Vm

router = Router(name=__name__)


@router.message(F.text, Command("start"))
async def start(message: Message) -> None:
    banner = await get_banner_file_id()
    if banner:
        media = banner
    else:
        banner_path = Path(__file__).parent.parent / "media" / "banner.jpg"
        media = FSInputFile(banner_path, "banner.jpg")
    msg = await message.answer_photo(media, caption=i18n_default('M.PVE.MAIN'), reply_markup=main_proxmox_kb())

    if not banner:
        file_id = msg.photo[-1].file_id
        await set_banner_file_id(file_id)


@router.message(F.text, Command("get_db"))
async def get_json(message: Message) -> None:
    vms = await Vm.all().values()
    payload = html.escape(json.dumps(vms, ensure_ascii=False, default=str))
    await message.answer(text=f"<code>{payload}</code>")


@router.message(Command("set_db"))
async def cmd_set_db(message: Message, state: FSMContext):
    await message.answer(i18n_default("M.DB.SET_DB_HELP"))
    await state.set_state(DbStates.waiting_for_set_json)


@router.message(Command("merge_db"))
async def cmd_merge_db(message: Message, state: FSMContext):
    await message.answer(i18n_default("M.DB.MERGE_DB_HELP"))
    await state.set_state(DbStates.waiting_for_merge_json)

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import i18n_default
from bot.keyboards.proxmox_kbs import main_proxmox_kb
from core.settings import BANNER_FILE_ID

router = Router(name=__name__)


@router.message(F.text, Command("start"))
async def start(message: Message) -> None:
    await message.answer_photo(BANNER_FILE_ID, caption=i18n_default('M.PVE.MAIN'), reply_markup=main_proxmox_kb())
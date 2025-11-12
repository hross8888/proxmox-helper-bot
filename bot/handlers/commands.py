from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from bot import i18n_default
from bot.keyboards.proxmox_kbs import main_proxmox_kb
from core.db import get_banner_file_id

router = Router(name=__name__)


@router.message(F.text, Command("start"))
async def start(message: Message) -> None:
    banner = await get_banner_file_id()
    if banner:
        media = banner
    else:
        banner_path = Path(__file__).parent.parent / "media" / "banner.jpg"
        media = FSInputFile(banner_path, "banner.jpg")
    await message.answer_photo(media, caption=i18n_default('M.PVE.MAIN'), reply_markup=main_proxmox_kb())
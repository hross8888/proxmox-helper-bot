from venv import logger

from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.common_kbs import back_kb
from bot.pve.states import PveCreateStates, PveEditStates
from bot import i18n_default
from bot.keyboards.proxmox_kbs import *
from core.models import Vm
from services.pve import proxmox


def render_summary(data: dict) -> str:
    """Формирует блок <b>Ваш выбор:</b> с корректными ├ и └ для всех параметров"""
    items = []

    if template_name := data.get("template_name"):
        items.append(i18n_default("M.PVE.SUMMARY.TEMPLATE").format(value=template_name))

    if ram := data.get("memory"):
        ram_str = f"{int(ram / 1024)}GB" if ram % 1024 == 0 else f"{ram}MB"
        items.append(i18n_default("M.PVE.SUMMARY.RAM").format(value=ram_str))

    if cores := data.get("cores"):
        items.append(i18n_default("M.PVE.SUMMARY.CORES").format(value=cores))

    if disk := data.get("disk_gb"):
        items.append(i18n_default("M.PVE.SUMMARY.DISK").format(value=f"{disk}GB"))

    if vm_name := data.get("name"):
        items.append(i18n_default("M.PVE.SUMMARY.NAME").format(value=vm_name))

    if not items:
        return ""

    lines = []
    for i, text in enumerate(items):
        prefix = "└" if i == len(items) - 1 else "├"
        lines.append(f"{prefix} {text}")

    header = i18n_default("M.PVE.SUMMARY.HEADER")
    return f"{header}\n" + "\n".join(lines)



async def render_step(event: CallbackQuery | Message, state: FSMContext):
    """Рендер шага (универсальный)"""
    current = await state.get_state()
    data = await state.get_data()
    is_query = isinstance(event, CallbackQuery)
    message = event.message if is_query else event

    # определяем текст и клавиатуру
    # Создание новой тачки
    if current in [PveCreateStates.main.state, PveEditStates.main.state]:
        text = i18n_default("M.PVE.MAIN")
        markup = main_proxmox_kb()

    elif current == PveCreateStates.select_template.state:
        text = i18n_default("M.PVE.SELECT_TEMPLATE")
        vms = await proxmox.get_vm_list(templates_only=True)
        vms.sort(key=lambda t: t.name)
        markup = select_template_kb(vms)

    elif current == PveCreateStates.select_ram.state:
        text = i18n_default("M.PVE.SELECT_RAM")
        markup = select_ram_kb()


    elif current == PveCreateStates.select_cores.state:
        text = i18n_default("M.PVE.SELECT_CORES")
        markup = select_cores_kb()

    elif current == PveCreateStates.select_disk.state:
        text = i18n_default("M.PVE.SELECT_DISK")
        markup = select_disk_kb()

    elif current == PveCreateStates.input_name.state:
        text = i18n_default("M.PVE.SELECT_NAME")
        markup = back_kb()

    elif current == PveCreateStates.input_password.state:
        text = i18n_default("M.PVE.SELECT_PASSWORD")
        markup = back_kb()

    elif current == PveCreateStates.creating_vm.state:
        # text = i18n_default("M.PVE.CREATING_WM")
        text = ""
        markup = back_kb()

    ## Работа с существующими vm
    elif current == PveEditStates.vm_list.state:
        text = i18n_default("M.PVE.LIST_WM")
        vms = await proxmox.get_vm_list()
        vms.sort(key=lambda t: t.vmid, reverse=True)
        markup = vm_list_kb(vms)

    elif current == PveEditStates.target_vm.state:
        vm_id=data.get("target_vm_id")
        vm_info = await proxmox.vm_info(data.get("target_vm_id"))
        db_vm = await Vm.get_or_none(vm_id=vm_id)
        ip_addresses = db_vm.ip_address if db_vm else "<b>NOT IN DB</b>"
        password = db_vm.password if db_vm else "<b>NOT IN DB</b>"
        domain = db_vm.domain if db_vm else "<b>NOT IN DB</b>"

        text = i18n_default("M.PVE.TARGET_WM").format(
            id=vm_info.vmid,
            name=vm_info.name,
            status=vm_info.status,
            cpus=vm_info.cpus,
            cpu=vm_info.cpu_usage_percent,
            mem=vm_info.ram_usage_str,
            disk=vm_info.disk_usage_str,
            uptime=vm_info.uptime,
            domain=domain or "unset",
            ip_addresses=ip_addresses,
            password=password,

        )
        markup = vm_edit_kb(vm_info)

    else:
        raise ValueError("[render_step] invalid state")

    summary = render_summary(data)
    if summary:
        text = f"{summary}\n\n{text}"
    last_bot_message_id = data.get("last_bot_message_id")

    try:
        if is_query and message:
            await message.edit_caption(caption=text, reply_markup=markup)
            await state.update_data(last_bot_message_id=message.message_id)
        elif last_bot_message_id:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption=text,
                reply_markup=markup,
            )
        else:
            sent = await message.answer(text, reply_markup=markup)
            await state.update_data(last_bot_message_id=sent.message_id)

    except TelegramAPIError:
        logger.error("[render_step] Telegram API error")
        sent = await message.answer(text, reply_markup=markup)
        await state.update_data(last_bot_message_id=sent.message_id)

# def _get_states_list() -> list[str]:
#     """Возвращает список имён состояний в порядке объявления"""
#     states = [
#         v.state
#         for v in PveCreateStates.__dict__.values()
#         if isinstance(v, State)
#     ]
#     return states

def _get_states_list(current_state: str) -> list[str]:
    """Определяет StatesGroup по имени текущего состояния и возвращает список состояний в порядке объявления."""
    if not current_state or ":" not in current_state:
        return []

    group_name = current_state.split(":")[0]

    # ищем класс с таким именем среди всех известных групп
    for group in StatesGroup.__subclasses__():
        if group.__name__ == group_name:
            return [
                v.state
                for v in group.__dict__.values()
                if isinstance(v, State)
            ]

    return []

async def next_step(state: FSMContext):
    """Переходит к следующему состоянию автоматически"""
    current = await state.get_state()
    steps = _get_states_list(current)

    try:
        idx = steps.index(current)
        if idx + 1 < len(steps):
            await state.set_state(steps[idx + 1])
    except ValueError:
        pass


async def prev_step(state: FSMContext):
    """Переходит к предыдущему состоянию автоматически"""
    current = await state.get_state()
    steps = _get_states_list(current)

    try:
        idx = steps.index(current)
        if idx > 0:
            await state.set_state(steps[idx - 1])
    except ValueError:
        pass
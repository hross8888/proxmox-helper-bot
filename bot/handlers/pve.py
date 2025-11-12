import re
from asyncio import create_task

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot import i18n_default
from bot.background_tasks import background_delete_vm, background_create_domain, background_create_vm
from bot.handlers.common import handle_step
from bot.keyboards.callbacks import *
from bot.keyboards.types import *
from bot.pve.flow import render_step, next_step
from bot.pve.states import *
from bot.shema import CreateVmShema
from bot.utils.message_helper import delete_messages, temporary_message
from core.models import Vm

router = Router(name=__name__)


@router.callback_query(PveMainCallback.filter())
async def pve_main_kb_handler(query: CallbackQuery, callback_data: PveMainCallback, state: FSMContext):
    await query.answer()
    if callback_data.action == PveMainCallbackAction.create_new:
        await state.set_state(PveCreateStates.select_template)
        await render_step(query, state)

    elif callback_data.action == PveMainCallbackAction.all:
        await state.set_state(PveEditStates.vm_list)
        await render_step(query, state)


# Создание vm
@router.callback_query(PveTemplateCallback.filter())
async def pve_os_kb_handler(query: CallbackQuery, callback_data: PveTemplateCallback, state: FSMContext):
    await state.update_data(template_id=callback_data.template_id)
    await state.update_data(template_name=callback_data.template_name)
    await handle_step(query, state)


@router.callback_query(PveRamCallback.filter())
async def pve_ram_kb_handler(query: CallbackQuery, callback_data: PveRamCallback, state: FSMContext):
    await state.update_data(memory=callback_data.value_mb)
    await handle_step(query, state)


@router.callback_query(PveCoresCallback.filter())
async def pve_cores_kb_handler(query: CallbackQuery, callback_data: PveCoresCallback, state: FSMContext):
    await state.update_data(cores=callback_data.value_cores)
    await handle_step(query, state)


@router.callback_query(PveDiskCallback.filter())
async def pve_disk_kb_handler(query: CallbackQuery, callback_data: PveDiskCallback, state: FSMContext):
    await state.update_data(disk_gb=callback_data.memory)
    await handle_step(query, state)


@router.message(F.text, PveCreateStates.input_name)
async def input_server_name_handler(message: Message, bot: Bot, state: FSMContext):
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", message.text):
        msg = await message.answer(i18n_default("M.PVE.ERROR.VM_NAME"))
        await delete_messages(bot, [msg, message], 1)
        return

    if await Vm.filter(name=message.text).exists():
        msg = await message.answer(i18n_default("M.PVE.ERROR.VM_NAME_DUPLICATE"))
        await delete_messages(bot, [msg, message], 1)
        return

    await state.update_data(name=message.text)
    await delete_messages(bot, message, 0)
    await next_step(state)
    await render_step(message, state)


@router.message(F.text, PveCreateStates.input_password)
async def input_root_password_handler(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(password=message.text)
    await delete_messages(bot, message, 0)

    data = await state.get_data()
    vm_data = CreateVmShema(**data)

    await state.set_state(PveCreateStates.creating_vm)
    await render_step(message, state)

    create_task(background_create_vm(message=message, vm_data=vm_data))

    await temporary_message(message=message, text=i18n_default("M.PVE.CREATING_WM"))

    await state.set_state(PveEditStates.main)
    await render_step(message, state)
    await state.clear()


# Редактирование vm

@router.callback_query(PveListVmCallback.filter())
async def pve_disk_kb_handler(query: CallbackQuery, callback_data: PveListVmCallback, state: FSMContext):
    await state.update_data(target_vm_id=callback_data.vm_id)
    await handle_step(query, state)


@router.callback_query(PveEditVmCallback.filter())
async def pve_edit_vn_handler(query: CallbackQuery, callback_data: PveEditVmCallback, state: FSMContext):
    if callback_data.action == PveEditVmCallbackAction.create_domain:
        await state.update_data(target_vm_id=callback_data.vm_id)  # вдруг потеряли
        vm = await Vm.get_or_none(vm_id=callback_data.vm_id)
        if not vm:
            await query.answer(
                i18n_default("M.PVE.ERROR.VM_NOT_FOUND").format(vm_id=callback_data.vm_id),
                show_alert=True
            )
            return

        await query.answer(i18n_default("M.PVE.CREATING_DOMAIN"))

        create_task(background_create_domain(vm=vm, message=query.message))

        await state.set_state(PveEditStates.main)
        await render_step(query, state)

    elif callback_data.action == PveEditVmCallbackAction.delete:
        vm = await Vm.get_or_none(vm_id=callback_data.vm_id)

        if not vm:
            await query.answer(
                i18n_default("M.PVE.ERROR.VM_NOT_FOUND").format(vm_id=callback_data.vm_id),
                show_alert=True
            )
            return

        await query.answer(i18n_default("M.PVE.DELETING_WM"))
        create_task(background_delete_vm(vm=vm, message=query.message))

        await state.set_state(PveEditStates.main)
        await render_step(query, state)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.callbacks import *
from bot.keyboards.types import *
from bot.keyboards.utils import arrange_keyboard
from core.models import Vm
from services.pve.shema import VmInfo, VmStatus


def main_proxmox_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Новая vm", callback_data=PveMainCallback(action=PveMainCallbackAction.create_new))
    builder.button(text="Все vm", callback_data=PveMainCallback(action=PveMainCallbackAction.all))

    builder.adjust(1)
    return builder.as_markup()


def select_template_kb(templates: list[VmInfo], rows=1):
    builder = InlineKeyboardBuilder()
    for template in templates:
        builder.button(
            text=template.name,
            callback_data=PveTemplateCallback(template_id=template.vmid, template_name=template.name)
        )

    builder.button(text="Назад", callback_data=BackCallback())

    arrange_keyboard(builder, total_buttons=len(templates), per_row=rows)
    return builder.as_markup()


def select_ram_kb(rows=3):
    builder = InlineKeyboardBuilder()
    ram_variants = [1024, 2048, 3072, 4096, 6144, 8192, 12288, 16384, 32768]

    for mb in ram_variants:
        gb = int(mb / 1024)
        builder.button(text=f"{gb} GB", callback_data=PveRamCallback(value_mb=mb))

    builder.button(text="Назад", callback_data=BackCallback())

    arrange_keyboard(builder, total_buttons=len(ram_variants), per_row=rows)
    return builder.as_markup()


def select_cores_kb(rows=4):
    builder = InlineKeyboardBuilder()
    core_variants = list(range(1, 29))

    for num in core_variants:
        builder.button(text=str(num), callback_data=PveCoresCallback(value_cores=num))

    builder.button(text="Назад", callback_data=BackCallback())

    arrange_keyboard(builder, total_buttons=len(core_variants), per_row=rows)
    return builder.as_markup()


def select_disk_kb(rows=4):
    builder = InlineKeyboardBuilder()
    memory_variants = list(range(10, 90, 10))
    for gb in memory_variants:
        builder.button(text=f"{gb} GB", callback_data=PveDiskCallback(memory=gb))

    builder.button(text="Назад", callback_data=BackCallback())
    arrange_keyboard(builder, total_buttons=len(memory_variants), per_row=rows)
    return builder.as_markup()


def vm_list_kb(vms: list[VmInfo], rows=2):
    builder = InlineKeyboardBuilder()
    max_len = max(len(vm.name) for vm in vms)
    for vm in vms:
        label = "▫️" if vm.status == VmStatus.running else "▪️"
        # invisible_needed = min(14, max(0, max_len - len(vm.name)))
        builder.button(
            text=f"{label}     {vm.name} ({vm.vmid})",
            callback_data=PveListVmCallback(vm_id=vm.vmid, vm_name=vm.name)
        )

    builder.button(text="Назад", callback_data=BackCallback())
    arrange_keyboard(builder, total_buttons=len(vms), per_row=rows)
    return builder.as_markup()


# def vm_list_kb(vms: list[VmInfo], rows=2):
#     from aiogram.utils.keyboard import InlineKeyboardBuilder
#
#     builder = InlineKeyboardBuilder()
#
#     # "веса" только для латиницы, цифр и тире
#     widths = {
#         "ilI"                 : 0.5,   # узкие
#         "ftjrs"               : 0.7,
#         "abcdeghknopquvyxz"   : 1.0,   # средние
#         "mwMW"                : 1.5,   # широкие
#         "ABCDEFGHIJKLMNOPQRSTUVWXYZ" : 1.2,  # заглавные
#         "0123456789-"         : 1.1,   # цифры и тире
#     }
#
#     def visual_width(name: str) -> float:
#         total = 0
#         for c in name:
#             for group, w in widths.items():
#                 if c in group:
#                     total += w
#                     break
#             else:
#                 total += 1.0
#         return total
#
#     max_width = max(visual_width(vm.name) for vm in vms)
#
#     for vm in vms:
#         label = "🟢" if vm.status == VmStatus.running else "🔴"
#         width_diff = max_width - visual_width(vm.name)
#         invisible_needed = int(width_diff * 1.1)
#
#         builder.button(
#             text=f"{label}   {' ' * invisible_needed}{vm.name}",
#             callback_data=PveListVmCallback(vm_id=vm.vmid, vm_name=vm.name)
#         )
#
#     builder.button(text="Назад", callback_data=BackCallback())
#     arrange_keyboard(builder, total_buttons=len(vms), per_row=rows)
#     return builder.as_markup()

def vm_edit_kb(vm: VmInfo):
    builder = InlineKeyboardBuilder()
    if vm.status == VmStatus.running:
        builder.button(
            text="Nginx", callback_data=PveEditVmCallback(vm_id=vm.vmid, action=PveEditVmCallbackAction.nginx)
        )
        builder.button(
            text="🌀 Перезапустить",
            callback_data=PveEditVmCallback(vm_id=vm.vmid, action=PveEditVmCallbackAction.reboot)
        )
        # builder.button(
        #     text="📃 Установить конфиг Nginx", callback_data=PveEditVmCallback(vm_id=vm.vmid, action=PveEditVmCallbackAction.set_conf_nginx)
        # )
        # builder.button(
        #     text="♻️ Перезапустить Nginx",
        #     callback_data=PveEditVmCallback(vm_id=vm.vmid, action=PveEditVmCallbackAction.reload_nginx)
        # )
        builder.button(
            text="🔅 Выключить", callback_data=PveEditVmCallback(vm_id=vm.vmid, action=PveEditVmCallbackAction.off)
        )
    else:
        builder.button(
            text="🔆 Включить", callback_data=PveEditVmCallback(vm_id=vm.vmid, action=PveEditVmCallbackAction.on)
        )
    # builder.button(
    #     text="🌐 Создать домен",
    #     callback_data=PveEditVmCallback(vm_id=vm.vmid, action=PveEditVmCallbackAction.create_domain)
    # )
    builder.button(
        text="⛔️ Удалить VM", callback_data=PveEditVmCallback(vm_id=vm.vmid, action=PveEditVmCallbackAction.delete)
    )
    builder.button(text="Назад", callback_data=BackCallback())
    builder.adjust(1)
    return builder.as_markup()



def vm_nginx_kb(db_vm: Vm):
    builder = InlineKeyboardBuilder()
    if not db_vm.domain:
        builder.button(
            text="🌐 Создать домен",
            callback_data=PveNginxCallback(vm_id=db_vm.vm_id, action=PveNginxCallbackAction.create_domain)
        )
    else:
        builder.button(
            text="✂️ Удалить домен",
            callback_data=PveNginxCallback(vm_id=db_vm.vm_id, action=PveNginxCallbackAction.delete_domain)
        )
        builder.button(
            text="📤 Прочитать конфиг",
            callback_data=PveNginxCallback(vm_id=db_vm.vm_id, action=PveNginxCallbackAction.get_conf_nginx)
        )
        builder.button(
            text="📥 Установить конфиг",
            callback_data=PveNginxCallback(vm_id=db_vm.vm_id, action=PveNginxCallbackAction.set_conf_nginx)
        )
        builder.button(
            text="♻️ Перезапустить Nginx",
            callback_data=PveNginxCallback(vm_id=db_vm.vm_id, action=PveNginxCallbackAction.reload_nginx)
        )
    builder.button(text="Назад", callback_data=BackCallback())
    builder.adjust(1)
    return builder.as_markup()
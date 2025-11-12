from aiogram.filters.callback_data import CallbackData

from bot.keyboards.types import *


class PveMainCallback(CallbackData, prefix="pve1"):
    action: PveMainCallbackAction


class PveTemplateCallback(CallbackData, prefix="pve2"):
    template_id: int
    template_name: str


class PveRamCallback(CallbackData, prefix="pve3"):
    value_mb: int


class PveCoresCallback(CallbackData, prefix="pve4"):
    value_cores: int


class PveDiskCallback(CallbackData, prefix="pve5"):
    memory: int


class PveListVmCallback(CallbackData, prefix="pve6"):
    vm_id: int
    vm_name: str


class PveEditVmCallback(CallbackData, prefix="pve7"):
    vm_id: int
    action: PveEditVmCallbackAction


class BackCallback(CallbackData, prefix="cmn1"):
    pass

class CloseCallback(CallbackData, prefix="cmn2"):
    pass

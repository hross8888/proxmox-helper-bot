from enum import Enum


class PveMainCallbackAction(int, Enum):
    create_new = 1
    all = 2


class PveEditVmCallbackAction(int, Enum):
    reboot = 0
    off = 1
    on = 2
    create_domain = 3
    delete = 4
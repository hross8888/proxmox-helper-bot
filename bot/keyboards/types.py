from enum import Enum


class PveMainCallbackAction(int, Enum):
    create_new = 1
    all = 2


class PveEditVmCallbackAction(int, Enum):
    reboot = 0
    off = 1
    on = 2
    nginx = 3
    delete = 4

class PveNginxCallbackAction(int, Enum):
    create_domain = 1
    delete_domain = 2
    reload_nginx = 3
    set_conf_nginx = 4
    get_conf_nginx = 5

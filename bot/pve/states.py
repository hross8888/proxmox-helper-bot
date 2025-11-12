from aiogram.fsm.state import StatesGroup, State


class PveCreateStates(StatesGroup):
    main = State()
    select_template = State()
    select_ram = State()
    select_cores = State()
    select_disk = State()
    input_name = State()
    input_password = State()
    creating_vm = State()

class PveEditStates(StatesGroup):
    main = State()
    vm_list = State()
    target_vm = State()
    nginx_conf = State()

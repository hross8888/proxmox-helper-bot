from aiogram.fsm.state import State, StatesGroup


class FcmState(StatesGroup):
    input_name = State()
    input_pass = State()
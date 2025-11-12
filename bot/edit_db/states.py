from aiogram.fsm.state import StatesGroup, State

class DbStates(StatesGroup):
    waiting_for_set_json = State()
    waiting_for_merge_json = State()
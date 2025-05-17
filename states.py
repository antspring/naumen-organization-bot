from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    profile_loaded = State()
    registration = State()
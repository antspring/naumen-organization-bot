from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    profile_loaded = State()
    registration = State()


class EventStates(StatesGroup):
    set_name = State()
    set_description = State()
    set_map = State()
    set_schedule = State()
    set_start_date = State()
    set_start_time = State()
    set_end_date = State()
    set_end_time = State()
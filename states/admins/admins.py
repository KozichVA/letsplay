from aiogram.fsm.state import StatesGroup, State


class GameAdminStatesGroup(StatesGroup):
    name = State()
    player_max_count = State()
    price = State()

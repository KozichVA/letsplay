from aiogram.fsm.state import StatesGroup, State


class GameAdminStatesGroup(StatesGroup):
    name = State()
    picture = State()
    description = State()
    rules = State()
    price = State()
    difficulty_level = State()
    player_max_count = State()




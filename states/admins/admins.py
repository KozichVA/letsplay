from aiogram.fsm.state import StatesGroup, State


class GameAdminStatesGroup(StatesGroup):
    name = State()
    picture = State()
    description = State()
    rules = State()
    difficulty_level = State()
    player_max_count = State()

class GameRoleStatesGroup(StatesGroup):
    role_name = State()
    description = State()
    gender = State()
    url = State()



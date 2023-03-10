from aiogram.fsm.state import StatesGroup, State


class GameAdminStatesGroup(StatesGroup):
    category_id = State()
    name = State()
    picture = State()
    description = State()
    rules = State()
    price = State()
    difficulty_level = State()
    player_max_count = State()
    game_id = State()
    edit = State()

class GameRoleStatesGroup(StatesGroup):
    game_id = State()
    role_name = State()
    role_description = State()
    gender = State()
    url = State()


class GameTagsStateGroup(StatesGroup):
    tag_id = State()
    tag_name = State()

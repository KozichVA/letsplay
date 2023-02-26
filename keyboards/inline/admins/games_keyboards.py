from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.models import Game, Category, Tag, GameRole


class GameListCallbackData(CallbackData, prefix='gp'):
    action: str = None
    game_id: int = None
    category_id: int = None
    tag_id: int = None
    tag_name: str = None
    role_id: int = None


async def category_list_ikb() -> InlineKeyboardMarkup:
    categories = await Category.all()
    buttons = [
        [
            InlineKeyboardButton(
                text=category.name,
                callback_data=GameListCallbackData(
                    action='all',
                    category_id=category.id
                ).pack()
            )
        ]
        for category in categories]
    buttons += [[InlineKeyboardButton(
                text='назад',
                callback_data=GameListCallbackData(
                    action='back_main_menu').pack())]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def game_list_ikb(category_id: int) -> InlineKeyboardMarkup:
    games = await Game.all(order_by='name', category_id=category_id)
    buttons = [
        [
            InlineKeyboardButton(
                text=game.name,
                callback_data=GameListCallbackData(
                    action='get_game',
                    game_id=game.id,
                    category_id=category_id
                ).pack()
            )
        ]
        for game in games
    ]
    buttons += [
        [
            InlineKeyboardButton(
                text='ДОБАВИТЬ',
                callback_data=GameListCallbackData(
                    action='add',
                    category_id=category_id
                ).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text='НАЗАД',
                callback_data=GameListCallbackData(
                    action='back_category'
                ).pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def game_detail_ikb(game_id: int) -> InlineKeyboardMarkup:
    game = await Game.get(pk=game_id)
    buttons = [
        [
            InlineKeyboardButton(
                text='РЕДАКТИРОВАТЬ',
                callback_data=GameListCallbackData(
                    action='edit',
                    game_id=game.id,
                    category_id=game.category_id
                ).pack()
            ),
            InlineKeyboardButton(
                text='УДАЛИТЬ',
                callback_data=GameListCallbackData(
                    action='del',
                    game_id=game.id
                ).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text='НАЗАД',
                callback_data=GameListCallbackData(
                    action='all',
                    category_id=game.category_id
                ).pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def game_edit_list_ikb(game_id: int, category_id: int):
    buttons = [[InlineKeyboardButton(text='Название',
                                     callback_data=GameListCallbackData(
                                         action='edit_game_name',
                                         game_id=game_id,
                                         category_id=category_id
                                     ).pack()),
                InlineKeyboardButton(text='Описание',
                                     callback_data=GameListCallbackData(
                                         action='edit_description',
                                         game_id=game_id,
                                         category_id=category_id
                                     ).pack())
                ],
               [InlineKeyboardButton(text='Картинка',
                                     callback_data=GameListCallbackData(
                                         action='edit_picture',
                                         game_id=game_id,
                                         category_id=category_id
                                     ).pack()),
                InlineKeyboardButton(text='Правила',
                                     callback_data=GameListCallbackData(
                                          action='edit_rules',
                                          game_id=game_id,
                                          category_id=category_id).pack())
                ]]
    if category_id == 1:
        buttons += [[InlineKeyboardButton(text='Кол-во игроков',
                                          callback_data=GameListCallbackData(
                                              action='edit_player_max_count',
                                              game_id=game_id,
                                              category_id=category_id).pack()),
                     InlineKeyboardButton(text='Сложность игры',
                                          callback_data=GameListCallbackData(
                                              action='edit_difficulty_level',
                                              game_id=game_id,
                                              category_id=category_id).pack())]]
    else:
        buttons += [[InlineKeyboardButton(text='Роли',
                                          callback_data=GameListCallbackData(
                                             action='get_game_role_ikb',
                                             game_id=game_id,
                                             category_id=category_id).pack()),
                     InlineKeyboardButton(text='Стоимость',
                                          callback_data=GameListCallbackData(
                                              action='edit_price',
                                              game_id=game_id,
                                              category_id=category_id).pack())]]
    buttons += [[InlineKeyboardButton(text='Тег',
                                      callback_data=GameListCallbackData(
                                         action='edit_tag',
                                         game_id=game_id,
                                         category_id=category_id).pack()),
                InlineKeyboardButton(text='Назад',
                                     callback_data=GameListCallbackData(
                                         action='get_game',
                                         game_id=game_id,
                                         category_id=category_id).pack())]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def tag_list_ikb(category_id: int, game_id: int, state_data: dict = None) -> InlineKeyboardMarkup:
    if state_data is None:
        state_data = {}
    tags = await Tag.all(order_by='name', category_id=category_id)
    buttons = [[InlineKeyboardButton(
                text=tag.name if tag.id not in state_data.get('tag_id', []) else tag.name + ' ✅',
                callback_data=GameListCallbackData(
                    action='get_tag',
                    game_id=game_id,
                    category_id=category_id,
                    tag_id=tag.id,
                    tag_name=tag.name
                ).pack())] for tag in tags]
    if category_id == 1:
        buttons += [[InlineKeyboardButton(text='Дальше',
                                          callback_data=GameListCallbackData(
                                            action='save_tag',
                                            game_id=game_id,
                                            category_id=category_id).pack()
                                          )]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def game_role_ikb(game_id: int):
    roles = await GameRole.all(game_id=game_id)
    button = [[]]
    if roles:
        button = [[InlineKeyboardButton(text=role.name,
                                        callback_data=GameListCallbackData(
                                            action='get_game_role',
                                            game_id=game_id,
                                            category_id=2,
                                            role_id=role.id
                                        ).pack())] for role in roles]
    button += [[InlineKeyboardButton(text='Мастерская водная',
                                     callback_data=GameListCallbackData(
                                         action='add_master_role',
                                         game_id=game_id,
                                         category_id=2
                                     ).pack())],
               [InlineKeyboardButton(text='Добавить',
                                     callback_data=GameListCallbackData(
                                         action='add_game_role',
                                         game_id=game_id,
                                         category_id=2
                                     ).pack()),
                InlineKeyboardButton(text='Назад',
                                     callback_data=GameListCallbackData(
                                         action='back_games_list',
                                         game_id=game_id,
                                         category_id=2
                                     ).pack())]]
    return InlineKeyboardMarkup(inline_keyboard=button)


async def role_gender_ikb(game_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Мужсой',
                              callback_data=GameListCallbackData(
                                  action='men',
                                  game_id=game_id,
                                  category_id=2
                              ).pack())],
        [InlineKeyboardButton(text='Женский',
                              callback_data=GameListCallbackData(
                                  action='women',
                                  game_id=game_id,
                                  category_id=2
                              ).pack())],
        [InlineKeyboardButton(text='Унисекс',
                              callback_data=GameListCallbackData(
                                  action='sex',
                                  game_id=game_id,
                                  category_id=2
                              ).pack())]])


async def role_detail_ikb(role_id: int) -> InlineKeyboardMarkup:
    role = await GameRole.get(pk=role_id)
    buttons = [
        [
            InlineKeyboardButton(
                text='РЕДАКТИРОВАТЬ',
                callback_data=GameListCallbackData(
                    action='edit_role',
                    role_id=role.id,
                    category_id=2,
                    game_id=role.game_id
                ).pack()
            ),
            InlineKeyboardButton(
                text='УДАЛИТЬ',
                callback_data=GameListCallbackData(
                    action='del_role',
                    game_id=role.game_id,
                    role_id=role.id
                ).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text='НАЗАД',
                callback_data=GameListCallbackData(
                    action='get_game_role_ikb',
                    category_id=2,
                    game_id=role.game_id,
                    role_id=role.id
                ).pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

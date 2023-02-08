from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.models import Game, Category


class GameListCallbackData(CallbackData, prefix='gp'):
    action: str = None
    game_id: int = None
    category_id: int = None


async def game_list_ikb(category_id: int) -> InlineKeyboardMarkup:
    games = await Game.all(order_by='name', category_id=category_id)
    buttons = [
        [
            InlineKeyboardButton(
                text=game.name,
                callback_data=GameListCallbackData(
                    action='get',
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
                    action='back'
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
        for category in categories
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

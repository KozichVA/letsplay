from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def help_menu_user():
    add_RPG = InlineKeyboardMarkup([[InlineKeyboardButton(text='Регистрация')],
                                   [InlineKeyboardButton(text='Контакты')],
                                    [InlineKeyboardButton(text='Добавить категорию')],
                                    ])

    return add_RPG
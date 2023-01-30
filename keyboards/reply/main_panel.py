from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_panel = ReplyKeyboardMarkup(resize_keyboard=True,
                                 one_time_keyboard=False,
                                 keyboard=
                                 [[KeyboardButton(text='Ближайшие события'), KeyboardButton(text='Коллекция Игр')],
                                  [KeyboardButton(text='Забронировать стол'),
                                   KeyboardButton(text='Заказать Игру на праздник')]])


main_panel_admin = ReplyKeyboardMarkup(resize_keyboard=True,
                                 one_time_keyboard=True,
                                 keyboard=
                                 [[KeyboardButton(text='Ближайшие события'), KeyboardButton(text='Коллекция Игр')],
                                  [KeyboardButton(text='Создать событие'), KeyboardButton(text='Назначить мастера')],
                                  [KeyboardButton(text='Добавить ролевуху'), KeyboardButton(text='Добавить настолку')],
                                  [KeyboardButton(text='Сделать рассылку'), KeyboardButton(text='Утвердить роли')]])

main_panel_master = ReplyKeyboardMarkup(resize_keyboard=True,
                                 one_time_keyboard=False,
                                 keyboard=
                                 [[KeyboardButton(text='Ближайшие события'), KeyboardButton(text='Коллекция Игр')],
                                  [KeyboardButton(text='Забронировать стол'), KeyboardButton(text='Добавить игру')]])
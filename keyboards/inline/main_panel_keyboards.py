from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
# from utils.models import User


class StartPanelCallbackData(CallbackData, prefix='start_panel'):
    action: str = None
    # user_id: int = User.get(pk=Message.from_user.id)


async def user_start_panel() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text='Ближайшие события',
                              callback_data=StartPanelCallbackData(
                                  action='get_event'
                              ).pack()),
         InlineKeyboardButton(text='Коллекция игр',
                              callback_data=StartPanelCallbackData(
                                  action='get_game_list'
                              ).pack())],
        [InlineKeyboardButton(text='Забронировать стол',
                              callback_data=StartPanelCallbackData(
                                  action='take_table'
                              ).pack()),
         InlineKeyboardButton(text='Заказать игру на праздник',
                              callback_data=StartPanelCallbackData(
                                  action='order_event'
                              ).pack())],
        [InlineKeyboardButton(text='Регистрация',
                              callback_data=StartPanelCallbackData(
                                  action='registration'
                              ).pack()),
         InlineKeyboardButton(text='Скидки',
                              callback_data=StartPanelCallbackData(
                                  action='discount'
                              ).pack())],
        [InlineKeyboardButton(text='Официальный канал',
                              callback_data=StartPanelCallbackData(
                                  action='channel'
                              ).pack()),
         InlineKeyboardButton(text='Чат болталка',
                              callback_data=StartPanelCallbackData(
                                  action='chat'
                              ).pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def master_start_panel() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text='Ближайшие события',
                              callback_data=StartPanelCallbackData(
                                  action='get_event'
                              ).pack()),
         InlineKeyboardButton(text='Коллекция игр',
                              callback_data=StartPanelCallbackData(
                                  action='get_game_list'
                              ).pack())],
        [InlineKeyboardButton(text='Забронировать стол',
                              callback_data=StartPanelCallbackData(
                                  action='take_table'
                              ).pack()),
         InlineKeyboardButton(text='Заказать игру на праздник',
                              callback_data=StartPanelCallbackData(
                                  action='order_event'
                              ).pack())],
        [InlineKeyboardButton(text='Регистрация',
                              callback_data=StartPanelCallbackData(
                                  action='registration'
                              ).pack()),
         InlineKeyboardButton(text='Скидки',
                              callback_data=StartPanelCallbackData(
                                  action='discount'
                              ).pack())],
        [InlineKeyboardButton(text='Добавить игру',
                              callback_data=StartPanelCallbackData(
                                  action='add'
                              ).pack()),
         InlineKeyboardButton(text='Чат болталка',
                              callback_data=StartPanelCallbackData(
                                  action='get_my_game'
                              ).pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def admin_start_panel() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text='Ближайшие события',
                              callback_data=StartPanelCallbackData(
                                  action='get_event'
                              ).pack()),
         InlineKeyboardButton(text='Коллекция игр',
                              callback_data=StartPanelCallbackData(
                                  action='get_game_list'
                              ).pack())],
        [InlineKeyboardButton(text='Создать событие',
                              callback_data=StartPanelCallbackData(
                                  action='create_event'
                              ).pack()),
         InlineKeyboardButton(text='Назначить мастера',
                              callback_data=StartPanelCallbackData(
                                  action='add_master'
                              ).pack())],
        [InlineKeyboardButton(text='Изменить стоимость',
                              callback_data=StartPanelCallbackData(
                                  action='edit_category_price'
                              ).pack()),
         InlineKeyboardButton(text='Добавить Игру',
                              callback_data=StartPanelCallbackData(
                                  action='add_game'
                              ).pack())],
        [InlineKeyboardButton(text='Отправить приглашение',
                              callback_data=StartPanelCallbackData(
                                  action='send_invitation'
                              ).pack()),
         InlineKeyboardButton(text='Утвердить роли',
                              callback_data=StartPanelCallbackData(
                                  action='check_roles'
                              ).pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

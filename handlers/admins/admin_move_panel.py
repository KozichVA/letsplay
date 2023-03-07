from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline.admins import GameListCallbackData, category_list_ikb, game_list_ikb, game_edit_list_ikb
from keyboards.inline import admin_start_panel, master_start_panel, user_start_panel
from utils.models import User, Game

admin_move_router = Router(name='admin_move')


@admin_move_router.callback_query(GameListCallbackData.filter(F.action == 'back_category'))
async def get_categories_list(update: Message | CallbackQuery):
    if isinstance(update, Message):
        await update.delete()
        await update.edit_reply_markup(
            text='ВЫБЕРИТЕ КАТЕГОРИЮ',
            reply_markup=await category_list_ikb()
        )
    else:
        await update.message.edit_text(
            text='ВЫБЕРИТЕ КАТЕГОРИЮ',
            reply_markup=await category_list_ikb()
        )


@admin_move_router.callback_query(GameListCallbackData.filter(F.action == 'back_games_list'))
async def get_games_list(callback: CallbackQuery, callback_data: GameListCallbackData):
    await callback.message.delete()
    await callback.message.answer(
        text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
        reply_markup=await game_list_ikb(callback_data.category_id)
    )


@admin_move_router.callback_query(GameListCallbackData.filter(F.action == 'back_main_menu'))
async def get_main_menu(update: Message | CallbackQuery):
    user = await User.get(pk=update.from_user.id)
    text = f'Добро пожаловать, @{update.message.from_user.full_name} 😍\n' \
           f'Приветствую тебя в клубе настольных и ролевых игр - \n\"***Let’s play***\"!  \n' \
           f'Каждую неделю мы собираемся, чтобы классно провести время! 🥳'
    if user.role_id == 1:
        await update.message.edit_text(
            text=text,
            reply_markup=await admin_start_panel())
    elif user.role_id == 3:
        await update.message.edit_text(text=text, reply_markup=await master_start_panel())
    else:
        await update.message.edit_text(text=text, reply_markup=await user_start_panel())


@admin_move_router.callback_query(GameListCallbackData.filter(F.action == 'back_game_role_ikb'))
async def get_roles_list(callback: CallbackQuery, callback_data: GameListCallbackData):
    game = await Game.get(pk=callback_data.game_id)
    await callback.message.edit_text(
        text=f'Редактируем игру {game.name}',
        reply_markup=await game_edit_list_ikb(game_id=callback_data.game_id, category_id=callback_data.category_id)
    )


@admin_move_router.callback_query(GameListCallbackData.filter(F.action == 'back_game_list'))
async def get_roles_list(callback: CallbackQuery, callback_data: GameListCallbackData):
    game = await Game.get(pk=callback_data.game_id)
    await callback.message.edit_text(
        text=f'Редактируем игру {game.name}',
        reply_markup=await game_edit_list_ikb(game_id=callback_data.game_id, category_id=callback_data.category_id)
    )
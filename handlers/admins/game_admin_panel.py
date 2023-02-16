from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.exc import IntegrityError

from filters import IsAdminFilter
from keyboards.inline.admins import game_list_ikb, GameListCallbackData, category_list_ikb, game_detail_ikb,\
    game_edit_list_ikb, tag_list_ikb
from loader import bot
from states.admins import GameAdminStatesGroup
from utils.models import Game

game_panel_router = Router(name='game_panel')
game_panel_router.message.filter(IsAdminFilter())
game_panel_router.callback_query.filter(IsAdminFilter())


@game_panel_router.message(F.text == 'Добавить настолку')
async def get_BG_list(message: Message):
    await message.delete()
    await message.answer(
        text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
        reply_markup=await game_list_ikb(category_id=1))


@game_panel_router.message(F.text == 'Добавить ролевуху')
async def get_RPG_list(message: Message):
    await message.delete()
    await message.answer(
        text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
        reply_markup=await game_list_ikb(category_id=2))


@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'back'))
@game_panel_router.message(F.text.lower() == 'добавить')
async def get_categories_list(update: Message | CallbackQuery):
    if isinstance(update, Message):
        await update.delete()
        await update.answer(
            text='ВЫБЕРИТЕ КАТЕГОРИЮ',
            reply_markup=await category_list_ikb()
        )
    else:
        await update.message.edit_text(
            text='ВЫБЕРИТЕ КАТЕГОРИЮ',
            reply_markup=await category_list_ikb()
        )


@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'all'))
async def get_games_list(callback: CallbackQuery, callback_data: GameListCallbackData):
    await callback.message.answer(
        text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
        reply_markup=await game_list_ikb(callback_data.category_id)
    )


@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'get'))
async def get_game_info(callback: CallbackQuery, callback_data: GameListCallbackData):
    await callback.message.delete()
    game = await Game.get(pk=callback_data.game_id)
    if game.picture:
        await callback.message.answer_photo(
            photo=game.picture,
            caption=f'***{game.name}***\n{game.description}\n'
                    f'***Число игроков:*** {game.player_max_count}\n'
                    f'***Сложность:*** {game.difficulty_level}/10'
                    f'\n***Правила:***'
        )
    if game.rules:
        await callback.message.answer_document(
            document=game.rules,
            reply_markup=await game_detail_ikb(game_id=game.id)
        )


@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'del'))
async def delete_game(callback: CallbackQuery, callback_data: GameListCallbackData):
    game = await Game.get(pk=callback_data.game_id)
    await game.delete()
    await callback.message.delete()
    await callback.message.answer(
        text=f'ИГРА ***{game.name}*** УДАЛЕНА!',
        reply_markup=await game_list_ikb(category_id=game.category_id)
    )


@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'add'))
async def add_new_game(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext = None):
    await state.set_state(GameAdminStatesGroup.name)
    await state.update_data(category_id=callback_data.category_id)
    await callback.message.edit_text(
        text='ВВЕДИТЕ НАЗВАНИЕ ИГРЫ'
    )


@game_panel_router.message(GameAdminStatesGroup.name)
async def create_game(message: Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    await state.update_data(name=message.text.title())
    await state.set_state(GameAdminStatesGroup.picture)
    await message.answer(text='ДОБАВЬТЕ КАРТИНКУ ИГРЫ:')


@game_panel_router.message(GameAdminStatesGroup.picture)
async def add_game_picture(message: Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    if message.content_type == 'photo':
        await state.update_data(picture=message.photo[-1].file_id)
        await state.set_state(GameAdminStatesGroup.description)
        text = 'Добавьте описание игры!'
    else:
        text = 'Это не картинка, отправь картинку, падла!'
    await message.answer(text=text)


@game_panel_router.message(GameAdminStatesGroup.description)
async def add_game_description(message: Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    await state.update_data(description=message.text)
    await state.set_state(GameAdminStatesGroup.rules)
    if GameAdminStatesGroup.category_id == 1:
        await message.answer(text='ДОБАВЬТЕ "pdf" ФАЙЛИК С ПРАВИЛАМИ:')
    else:
        await message.answer(text='Правила ролевой игры сами добавляются и переходим к таблице с ролями')

@game_panel_router.message(GameAdminStatesGroup.rules)
async def add_game_rules(message: Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    if message.content_type == 'document':
        await state.update_data(rules=message.document.file_id)
        await state.set_state(GameAdminStatesGroup.difficulty_level)
        await message.answer(text='ДОБАВЬТЕ УРОВЕНЬ СЛОЖНОСТИ ИГРЫ ОТ 1 ДО 10')
    else:
        await message.answer(text='Это не документ')


@game_panel_router.message(GameAdminStatesGroup.difficulty_level)
async def add_difficulty_level(message: Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    if message.text.isdigit():
        await state.update_data(difficulty_level=int(message.text))
        await state.set_state(GameAdminStatesGroup.player_max_count)
        await message.answer('ВВЕДИТЕ КОЛИЧЕСТВО ИГРОКОВ')

    else:
        await message.answer(text='НЕВЕРНОЕ ЗНАЧЕНИЕ, ПРОВЕРЬТЕ И ПОВТОРИТЕ')


@game_panel_router.message(GameAdminStatesGroup.player_max_count)
async def add_player_max_count(message: Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    if message.text.isdigit():
        state_data = await state.get_data()
        await state.clear()
        game = Game(**state_data | {'player_max_count': int(message.text)})
        try:
            await game.save()
        except IntegrityError:
            text = 'Такая игра уже существует!'
        else:
            text = f'ИГРА ***{game.name}*** УСПЕШНО ДОБАВЛЕНА!!! \n Добавьте теги для фильтрации:'
        await message.answer(
            text=text,
            reply_markup=await tag_list_ikb(category_id=game.category_id, game_id=game.id)
            # reply_markup=await game_list_ikb(category_id=game.category_id)
        )
    else:
        await message.answer(
            text='НЕВЕРНОЕ ЗНАЧЕНИЕ, ПРОВЕРЬТЕ И ПОВТОРИТЕ'
        )


# @game_panel_router.message(GameAdminStatesGroup.category_id, GameAdminStatesGroup.g)
# async def add_tag(message: Message)
#     await message.answer(text='Присвоить игре теги:',
#                          reply_markup=await tag_list_ikb(category_id=))


@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'edit'))
async def edit_game(callback: CallbackQuery, callback_data: GameListCallbackData):
    game = await Game.get(pk=callback_data.game_id)
    await callback.message.delete()
    await callback.message.answer(
        text=f'Редактируем игру ***{game.name}***',
        reply_markup=await game_edit_list_ikb(game_id=game.id, category_id=game.category_id)
    )

@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'back_add_games'))
async def back_to_game_detail_ikb(callback: CallbackQuery, callback_data: GameListCallbackData):
    await callback.message.delete()
    await callback.message.answer(text='Выберите игру или добавьте новую:',
                                  reply_markup=await game_list_ikb(category_id=callback_data.category_id))


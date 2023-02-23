from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, callback_query, CallbackQuery
from sqlalchemy.exc import IntegrityError

from keyboards.inline.admins import game_list_ikb, category_list_ikb, GameListCallbackData, tag_list_ikb
from keyboards.inline import StartPanelCallbackData
from loader import bot
from states.admins import GameAdminStatesGroup
from utils.models import Game, Category

add_games_router = Router(name='add_games')


@add_games_router.message(F.text == 'Добавить настолку')
async def get_bg_list(message: Message):
    await message.delete()
    await message.answer(
        text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
        reply_markup=await game_list_ikb(category_id=1))


@add_games_router.message(F.text == 'Добавить ролевуху')
async def get_bg_list(message: Message):
    await message.delete()
    await message.answer(
        text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
        reply_markup=await game_list_ikb(category_id=2))


@add_games_router.callback_query(GameListCallbackData.filter(F.action == 'all'))
async def get_games_list(callback: CallbackQuery, callback_data: GameListCallbackData):
    await callback.message.answer(
        text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
        reply_markup=await game_list_ikb(callback_data.category_id)
    )


@add_games_router.callback_query(StartPanelCallbackData.filter(F.action == 'add_game'))
@add_games_router.message(F.text == 'Добавить игру')
async def get_categories_list(update: Message | CallbackQuery):
    if update.from_user.id == 3:
        await update.answer(text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
                            reply_markup=await game_list_ikb(category_id=2))
    else:
        if isinstance(update, Message):
            await update.delete()
            await update.answer(
                text='ВЫБЕРИТЕ КАТЕГОРИЮ',
                reply_markup=await category_list_ikb())
        else:
            await update.message.edit_text(
                text='ВЫБЕРИТЕ КАТЕГОРИЮ',
                reply_markup=await category_list_ikb())


@add_games_router.callback_query(GameListCallbackData.filter(F.action == 'add'))
async def add_new_game(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext = None):
    await state.set_state(GameAdminStatesGroup.name)
    await state.update_data(category_id=callback_data.category_id)
    await callback.message.edit_text(
        text='ВВЕДИТЕ НАЗВАНИЕ ИГРЫ'
    )


@add_games_router.message(GameAdminStatesGroup.name)
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


@add_games_router.message(GameAdminStatesGroup.picture)
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


@add_games_router.message(GameAdminStatesGroup.description)
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
    state_data = await state.get_data()
    if state_data.get('category_id') == 1:
        await message.answer(text='Добавьте \"pdf\" файл с правилами настольной игры:')
    else:
        await state.update_data(rules='https://telegra.ph/Kak-igrat-Rolevye-igry-zhivogo-dejstviya-02-23')
        state_data = await state.get_data()
        await state.clear()
        category = await Category.get(pk=state_data.get('category_id'))
        game = Game(category_id=state_data.get('category_id'),
                    name=state_data.get('name'),
                    picture=state_data.get('picture'),
                    description=state_data.get('description'),
                    rules=state_data.get('rules'),
                    price=category.price)
        try:
            await game.save()
        except IntegrityError:
            text = 'Такая игра уже существует!'
        else:
            text = f'ИГРА ***{game.name}*** УСПЕШНО ДОБАВЛЕНА!!! \n Добавьте теги для фильтрации:'
        await message.answer(
            text=text,
            reply_markup=await tag_list_ikb(category_id=game.category_id, game_id=game.id))


@add_games_router.message(GameAdminStatesGroup.rules)
async def add_rules(message: Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1)
    except TelegramBadRequest:
        pass
    if message.content_type == 'document':
        await state.update_data(rules=message.document.file_id)
        await state.set_state(GameAdminStatesGroup.difficulty_level)
        await message.answer(text='ДОБАВЬТЕ УРОВЕНЬ СЛОЖНОСТИ ИГРЫ ОТ 1 ДО 10')
    else:
        await message.answer(text='Это не документ')


@add_games_router.message(GameAdminStatesGroup.difficulty_level)
async def add_difficulty_level(message: Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1)
    except TelegramBadRequest:
        pass
    if message.text.isdigit():
        await state.update_data(difficulty_level=int(message.text))
        await state.set_state(GameAdminStatesGroup.player_max_count)
        await message.answer('ВВЕДИТЕ КОЛИЧЕСТВО ИГРОКОВ')

    else:
        await message.answer(text='НЕВЕРНОЕ ЗНАЧЕНИЕ, ПРОВЕРЬТЕ И ПОВТОРИТЕ')


@add_games_router.message(GameAdminStatesGroup.player_max_count)
async def add_player_max_count(message: Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1)
    except TelegramBadRequest:
        pass
    if message.text.isdigit():
        await state.update_data(player_max_count=int(message.text))
        state_data = await state.get_data()
        await state.clear()
        category = await Category.get(pk=state_data.get('category_id'))
        game = Game(category_id=state_data.get('category_id'),
                    name=state_data.get('name'),
                    picture=state_data.get('picture'),
                    description=state_data.get('description'),
                    rules=state_data.get('rules'),
                    price=category.price,
                    player_max_count=state_data.get('player_max_count'),
                    difficulty_level=state_data.get('difficulty_level'))
        try:
            await game.save()
        except IntegrityError:
            text = 'Такая игра уже существует!'
        else:
            text = f'ИГРА ***{game.name}*** УСПЕШНО ДОБАВЛЕНА!!! \n Добавьте теги для фильтрации:'
        await message.answer(
            text=text,
            reply_markup=await tag_list_ikb(category_id=game.category_id, game_id=game.id))
    else:
        await message.answer(text='НЕВЕРНОЕ ЗНАЧЕНИЕ, ПРОВЕРЬТЕ И ПОВТОРИТЕ')



@add_games_router.callback_query(GameListCallbackData.filter(F.action =='get_tag'))
async def get_teg()










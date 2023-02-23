from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.exc import IntegrityError

from filters import IsAdminFilter
from keyboards.inline.admins import game_list_ikb, GameListCallbackData, category_list_ikb, game_detail_ikb, \
    game_edit_list_ikb, tag_list_ikb, game_role_ikb, role_gender_ikb
from loader import bot
from states.admins import GameAdminStatesGroup, GameRoleStatesGroup
from utils.models import Game, GameTag, Tag, GameRole
from keyboards.inline import StartPanelCallbackData

game_panel_router = Router(name='game_panel')
game_panel_router.message.filter(IsAdminFilter())
game_panel_router.callback_query.filter(IsAdminFilter())


@game_panel_router.message(F.text == 'Добавить настолку')
async def get_bg_list(message: Message):
    await message.delete()
    await message.answer(
        text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
        reply_markup=await game_list_ikb(category_id=1))


@game_panel_router.message(F.text == 'Добавить ролевуху')
async def get_rpg_list(message: Message):
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


@game_panel_router.callback_query(StartPanelCallbackData.filter(F.action == 'add_game'))
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
    if game.category_id == 1:
        await callback.message.answer_photo(
            photo=game.picture,
            caption=f'***{game.name}***\n{game.description}\n'
                    f'***Число игроков:*** {game.player_max_count}\n'
                    f'***Сложность:*** {game.difficulty_level}/10'
                    f'\n***Правила:***'
        )
        await callback.message.answer_document(
            document=game.rules,
            reply_markup=await game_detail_ikb(game_id=game.id)
        )
    else:
        await callback.message.answer_photo(
            photo=game.picture,
            caption=f'***{game.name}***\n{game.description}\n',
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
    state_data = await state.get_data()
    game = Game(
        name=state_data.get('name'),
        category_id=state_data.get('category_id'),
        description=state_data.get('description')


    )
    try:
        await game.save()
    except IntegrityError:
        text = 'Такая игра уже существует.'
        reply_markup = await game_list_ikb(category_id=game.category_id)
    else:
        text = f'Игра ***{game.name}*** успешно добавлена!'
        reply_markup = await tag_list_ikb(category_id=game.category_id, game_id=game.id)
    await message.answer(text=text, reply_markup=reply_markup)


@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'get_tag'))
async def get_tag(callback: CallbackQuery, callback_data: GameListCallbackData):
    if callback_data.category_id == 2:
        game_tag = GameTag(game_id=callback_data.game_id, tag_id=callback_data.tag_id)
        await game_tag.save()
        await callback.message.answer(text='Тег добавлен! Добавить роль:',
                                      reply_markup=await game_role_ikb(callback_data.game_id))
    else:
        game_tag = GameTag(game_id=callback_data.game_id, tag_id=callback_data.tag_id)
        # tag_name = Tag.name
        tag_name = Tag.get(pk=callback_data.tag_id)
        try:
            await game_tag.save()
            await callback.message.answer(text=f'Тег ***{tag_name}*** добавлен!')
        except IntegrityError:
            await game_tag.delete()
            await callback.message.answer(text=f'Тег ***{tag_name}*** удалён!')
        await callback.message.answer(text='Выберите теги для настольной игры:',
                                      reply_markup=await tag_list_ikb(category_id=callback_data.category_id,
                                                                      game_id=callback_data.game_id))


@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'back_RPG'))
async def back_rpg(callback: CallbackQuery):
    await callback.message.answer(text='Выберите игру или добавьте новую:',
                                  reply_markup=await game_list_ikb(category_id=2))


@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'next'))
async def save_tag(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GameAdminStatesGroup.rules)
    await callback.message.answer(text='Добавьте \"pdf\" файл с правилами настольной игры:')


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
        await state.update_data(player_max_count=int(message.text))
        state_data = await state.get_data()
        await state.clear()
        # game = Game(**state_data | {'player_max_count': int(message.text)})
        game = Game(player_max_count=state_data.get('player_max_count'),
                    rules=state_data.get('rules'),
                    difficulty_level=state_data.get('difficulty_level')
                    )
        try:
            await game.save()
        except IntegrityError:
            text = 'Такая игра уже существует!'
        else:
            text = f'ИГРА ***{game.name}*** УСПЕШНО ДОБАВЛЕНА!!! \n Добавьте теги для фильтрации:'
        await message.answer(
            text=text,
            reply_markup=await game_list_ikb(category_id=game.category_id)
        )
    else:
        await message.answer(
            text='НЕВЕРНОЕ ЗНАЧЕНИЕ, ПРОВЕРЬТЕ И ПОВТОРИТЕ'
        )


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


@game_panel_router.callback_query(GameListCallbackData.filter(F.action == 'add_game_role'))
async def add_game_role(callback: CallbackQuery, state: FSMContext,):
    await callback.message.delete()
    await state.set_state(GameRoleStatesGroup.role_name)
    await callback.message.answer(text='Введите имя персонажа:')


@game_panel_router.message(GameRoleStatesGroup.role_name)
async def add_role_name(message: Message, state: FSMContext):
    # await message.delete()
    await state.update_data(role_name=message.text)
    await state.set_state(GameRoleStatesGroup.role_description)
    await message.answer(text='Введите ***краткое*** описание персонажа:')


@game_panel_router.message(GameRoleStatesGroup.role_description)
async def add_role_description(message: Message, state: FSMContext, callback_data: GameListCallbackData):
    await message.delete()
    await state.update_data(role_description=message.text)
    await state.set_state(GameRoleStatesGroup.gender)
    await message.answer(text='Выберите пол персонажа:',
                         reply_markup=await role_gender_ikb(game_id=callback_data.game_id))


@game_panel_router.message(GameListCallbackData.filter(F.action == 'men'))
@game_panel_router.message(GameRoleStatesGroup.gender)
async def add_gener(state: FSMContext, callback: CallbackQuery):
    await callback.message.delete()
    await state.set_state(GameRoleStatesGroup.url)
    await state.update_data(gender=True)
    await callback.message.edit_text(text='Введите сылочку на роль в telegra.ph:')


@game_panel_router.message(GameRoleStatesGroup.url)
async def add_url(message: Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    await state.update_data(url=message.text)
    state_data = await state.get_data()
    await state.clear()
    role = GameRole(name=state_data.get('role_name'),
                    is_man=state_data.get('gender'),
                    description=state_data.get('role_description'),
                    url=state_data.get('url'))
    try:
        await role.save()
    except IntegrityError:
        text = 'Такая игра уже существует!'
    else:
        text = f'ИГРА ***{role.name}*** УСПЕШНО ДОБАВЛЕНА!!!'
    await message.answer(
        text=text,
        reply_markup=await game_role_ikb(game_id=GameListCallbackData.game_id))

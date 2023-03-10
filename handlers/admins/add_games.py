from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.exc import IntegrityError

from keyboards.inline.admins import game_list_ikb, category_list_ikb, GameListCallbackData, \
    tag_list_ikb, game_role_ikb, role_gender_ikb
from keyboards.inline import StartPanelCallbackData
from loader import bot
from states.admins import GameAdminStatesGroup
from states.admins.admins import GameTagsStateGroup, GameRoleStatesGroup
from utils.models import Game, Category, GameTag, GameRole

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
    await callback.message.edit_text(
        text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
        reply_markup=await game_list_ikb(callback_data.category_id)
    )


@add_games_router.callback_query(StartPanelCallbackData.filter(F.action == 'add_game'))
@add_games_router.message(F.text == 'Добавить игру')
async def get_categories_list(update: Message | CallbackQuery):
    if update.from_user.id == 3:
        await update.message.edit_text(text='ВЫБЕРИТЕ ИГРУ ИЛИ ДОБАВЬТЕ НОВУЮ',
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
            await state.set_state(GameTagsStateGroup.tag_id)
            await state.update_data(tag_id=[])
        await message.answer(
            text=text,
            reply_markup=await tag_list_ikb(category_id=game.category_id, game_id=game.id))
    else:
        await message.answer(text='НЕВЕРНОЕ ЗНАЧЕНИЕ, ПРОВЕРЬТЕ И ПОВТОРИТЕ')


@add_games_router.callback_query(GameListCallbackData.filter(F.action == 'get_tag'))
async def get_teg(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext):
    if callback_data.category_id == 2:
        game_tag = GameTag(game_id=callback_data.game_id, tag_id=callback_data.tag_id)
        await game_tag.save()
        await callback.message.edit_text(text=f'Тег ***{callback_data.tag_name}*** добавлен! Добавить роль:',
                                         reply_markup=await game_role_ikb(callback_data.game_id))
    else:
        state_data = await state.get_data()
        if callback_data.tag_id in state_data.get('tag_id'):
            state_data['tag_id'].remove(callback_data.tag_id)
        else:
            state_data['tag_id'].append(callback_data.tag_id)
        await state.update_data(tags_id=state_data.get('tag_id'))
        await callback.message.edit_reply_markup(
            reply_markup=await tag_list_ikb(category_id=callback_data.category_id,
                                            game_id=callback_data.game_id,
                                            state_data=state_data)
        )


@add_games_router.callback_query(GameListCallbackData.filter(F.action == 'save_tag'))
async def save_tag(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext):
    state_data = await state.get_data()
    tags_id = state_data.get('tag_id')
    if tags_id:
        await state.clear()
        for tag_id in tags_id:
            game_tag = GameTag(game_id=callback_data.game_id, tag_id=tag_id)
            await game_tag.save()

        await callback.message.edit_text(
            text='Теги добавлены!',
            reply_markup=await game_list_ikb(
                category_id=callback_data.category_id
            )
        )
    else:
        await callback.message.answer(text='Ты забыл выбрать ***\"Тег\"***,'
                                           'поробуй ещё раз:',
                                      reply_markup=await tag_list_ikb(category_id=callback_data.category_id,
                                                                      game_id=callback_data.game_id))


@add_games_router.callback_query(GameListCallbackData.filter(F.action == 'add_game_role'))
async def add_game_role(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext, ):
    await callback.message.delete()
    await state.set_state(GameRoleStatesGroup.game_id)
    await state.update_data(game_id=callback_data.game_id)
    await state.set_state(GameRoleStatesGroup.role_name)
    await callback.message.answer(text='Введите имя персонажа:')


@add_games_router.message(GameRoleStatesGroup.role_name)
async def add_role_name(message: Message, state: FSMContext):
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    await message.delete()
    await state.update_data(role_name=message.text)
    await state.set_state(GameRoleStatesGroup.role_description)
    await message.answer(text='Введите ***краткое*** описание персонажа:')


@add_games_router.message(GameRoleStatesGroup.role_description)
async def add_role_description(message: Message, state: FSMContext):
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    await message.delete()
    await state.update_data(role_description=message.text)
    await state.set_state(GameRoleStatesGroup.gender)
    state_data = await state.get_data()
    await message.answer(text='Выберите пол персонажа, если это важно:',
                         reply_markup=await role_gender_ikb(game_id=state_data.get('game_id')))


@add_games_router.callback_query(GameListCallbackData.filter(F.action == 'men'))
async def add_gender(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(gender=True)
    await state.set_state(GameRoleStatesGroup.url)
    await callback.message.answer(text='Добавили мужика.\nВведите сылочку на роль в telegra.ph:')


@add_games_router.callback_query(GameListCallbackData.filter(F.action == 'women'))
async def add_gender(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(gender=False)
    await state.set_state(GameRoleStatesGroup.url)
    await callback.message.answer(text='Добавили жещину.\nВведите сылочку на роль в telegra.ph:')


@add_games_router.callback_query(GameListCallbackData.filter(F.action == 'sex'))
async def add_gender(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(gender=None)
    await state.set_state(GameRoleStatesGroup.url)
    await callback.message.answer(text='Добавили гемофродита.\nВведите сылочку на роль в telegra.ph:')


@add_games_router.message(GameRoleStatesGroup.url)
async def add_url(message: Message, state: FSMContext):
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    await message.delete()
    await state.update_data(url=message.text)
    state_data = await state.get_data()
    await state.clear()
    role = GameRole(name=state_data.get('role_name'),
                    is_man=state_data.get('gender'),
                    description=state_data.get('role_description'),
                    url=state_data.get('url'),
                    game_id=state_data.get('game_id'))

    try:
        await role.save()
    except IntegrityError:
        text = f'Персонаж ***{role.name}*** уже существует!, {role.description}, {role.is_man}, {role.url}'
    else:
        text = f'РОЛЬ ***{role.name}*** УСПЕШНО ДОБАВЛЕНА!!!'
        roles = await GameRole.all(game_id=state_data.get('game_id'))
        player_max_count = []
        for i in roles:
            player_max_count.append(i)
        game = await Game.get(pk=state_data.get('game_id'))
        game.player_max_count = len(player_max_count)
        await game.save()
    await message.answer(
        text=text,
        reply_markup=await game_role_ikb(game_id=role.game_id))


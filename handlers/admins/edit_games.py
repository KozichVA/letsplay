from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards.inline.admins import GameListCallbackData, game_detail_ikb, game_list_ikb, game_edit_list_ikb, \
    game_role_ikb
from keyboards.inline.admins.games_keyboards import role_detail_ikb, tag_list_ikb
from loader import bot
from states.admins.admins import GameAdminStatesGroup
from utils.models import Game, GameRole, Tag, GameTag

edit_game_router = Router(name='edit_game')


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'get_game'))
async def get_game_info(callback: CallbackQuery, callback_data: GameListCallbackData):
    await callback.message.delete()
    game = await Game.get(pk=callback_data.game_id)
    tags = [await Tag.get(pk=tag.tag_id) for tag in await GameTag.all(game_id=game.id)]
    if game.category_id == 1:
        await callback.message.answer_photo(
            photo=game.picture,
            caption=f'***{game.name}***\n'
                    f'{game.description}\n'
                    f'***Число игроков:*** {game.player_max_count}\n'
                    f'***Сложность:*** {game.difficulty_level}/10\n'
                    f'***Стоиомсть:*** {game.price} руб.\n'
                    f'***Теги:*** {", ".join(tag.name for tag in tags)}\n'
                    f'***Правила:***'
            )
        await callback.message.answer_document(
            document=game.rules,
            reply_markup=await game_detail_ikb(game_id=game.id))
    else:
        await callback.message.answer_photo(
            photo=game.picture,
            caption=f'***{game.name}***\n'
                    f'***Описание:*** {game.description}\n'
                    f'***Число игроков:*** \n'
                    f'***Стоиомость:*** {game.price} руб.\n'
                    f'***Как играть:*** {game.rules}\n'
                    f'***Тег:*** {", ".join(tag.name for tag in tags)}',
            reply_markup=await game_detail_ikb(game_id=game.id))


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'del'))
async def delete_game(callback: CallbackQuery, callback_data: GameListCallbackData):
    game = await Game.get(pk=callback_data.game_id)
    await game.delete()
    await callback.message.delete()
    await callback.message.answer(
        text=f'ИГРА ***{game.name}*** УДАЛЕНА!',
        reply_markup=await game_list_ikb(category_id=game.category_id))


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'edit'))
async def edit_game(callback: CallbackQuery, callback_data: GameListCallbackData):
    game = await Game.get(pk=callback_data.game_id)
    await callback.message.delete()
    await callback.message.answer(
        text=f'Редактируем игру ***{game.name}***',
        reply_markup=await game_edit_list_ikb(game_id=game.id, category_id=game.category_id))


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'edit_game_name'))
async def edit_game_name(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext):
    await callback.message.delete()
    game = await Game.get(pk=callback_data.game_id)
    await state.set_state(GameAdminStatesGroup.game_id)
    await state.update_data(game_id=game.id)
    await state.update_data(edit='name')
    await callback.message.answer(text=f'Меняем название игры ***{game.name}***\n'
                                       f'Введите новое название:')


@edit_game_router.message(GameAdminStatesGroup.game_id)
async def add_new_game_name(message: Message, state: FSMContext):
    try:
        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        pass
    await message.delete()
    state_data = await state.get_data()
    await state.clear()
    game_id = state_data.get('game_id')
    game = await Game.get(pk=game_id)
    if state_data.get('edit') == 'name':
        old_name = game.name
        game.name = message.text
        await game.save()
        await state.clear()
        await message.answer(text=f'Название игры ***{old_name}*** измененно на ***{game.name}***',
                             reply_markup=await game_edit_list_ikb(game_id=game.id, category_id=game.category_id))
    # --------------------------------------------------------------------------------------------------------------
    elif state_data.get('edit') == 'description':
        game.description = message.text
        await game.save()
        await state.clear()
        await message.answer(text=f'Описание игры ***{game.name}*** измененно!',
                             reply_markup=await game_edit_list_ikb(game_id=game.id, category_id=game.category_id))

    # _________________________________________________________________________________________________________________
    elif state_data.get('edit') == 'picture':
        if message.content_type == 'photo':
            game.picture = message.photo[-1].file_id
            await game.save()
            await state.clear()
            text = f'Изображение игры **{game.name}** измененно.'
        else:
            text = 'Это не картинка, отправь картинку, падла!'
        await message.answer(text=text,
                             reply_markup=await game_edit_list_ikb(game_id=game.id, category_id=game.category_id))

    # ________________________________________________________________________________________________________________
    elif state_data.get('edit') == 'rules':
        if message.content_type == 'document':
            game.rules = message.document.file_id
            await game.save()
            await state.clear()
            text = f'Правила игры **{game.name}** изменены.'
        else:
            text = f'Это не документ, отправь \"PDF!\" файлик с правилами игры ***{game.name}***'
        await message.answer(text=text,
                             reply_markup=await game_edit_list_ikb(game_id=game.id, category_id=game.category_id))

    # ________________________________________________________________________________________________________________
    elif state_data.get('edit') == 'player_max_count':
        if message.text.isdigit():
            game.player_max_count = int(message.text)
            await game.save()
            await state.clear()
            text = f'Максимальное количество игроков в игре **{game.name}** изменено.\n' \
                   f'Теперь кол-во игроков = **{game.player_max_count}**.'
        else:
            text = f'Это не цифра!!!\n' \
                   f'Введи максимальное количество игроков в игре ***{game.name}***:'
        await message.answer(text=text,
                             reply_markup=await game_edit_list_ikb(game_id=game.id, category_id=game.category_id))

    # _________________________________________________________________________________________________________

    elif state_data.get('edit') == 'difficulty_level':
        if message.text.isdigit():
            game.difficulty_level = int(message.text)
            await game.save()
            await state.clear()
            text = f'Уровень сложности игры **{game.name}** изменён на **{game.difficulty_level}**.'
        else:
            text = f'Это не цифра, сложность игры***{game.name}*** по шкале от 1 до 10'
        await message.answer(text=text,
                             reply_markup=await game_edit_list_ikb(game_id=game.id, category_id=game.category_id))
    else:
        await message.answer(text='Срабатывает условие для месенджей',
                             reply_markup=await game_edit_list_ikb(game_id=game.id, category_id=game.category_id))


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'edit_description'))
async def edit_game_description(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext):
    await callback.message.delete()
    game = await Game.get(pk=callback_data.game_id)
    await state.set_state(GameAdminStatesGroup.game_id)
    await state.update_data(game_id=game.id)
    await state.update_data(edit='description')
    await callback.message.answer(text=f'Меняем описание игры ***{game.name}***\n'
                                       f'Введите новое описание:')


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'edit_picture'))
async def edit_game_description(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext):
    await callback.message.delete()
    game = await Game.get(pk=callback_data.game_id)
    await state.set_state(GameAdminStatesGroup.game_id)
    await state.update_data(game_id=game.id)
    await state.update_data(edit='picture')
    await callback.message.answer(text=f'Меняем ***изображение*** игры ***{game.name}***\n'
                                       f'Добавьте картинку:')


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'edit_rules'))
async def edit_game_description(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext):
    await callback.message.delete()
    game = await Game.get(pk=callback_data.game_id)
    await state.set_state(GameAdminStatesGroup.game_id)
    await state.update_data(game_id=game.id)
    await state.update_data(edit='rules')
    await callback.message.answer(text=f'Меняем ***правила*** игры ***{game.name}***\n'
                                       f'Добавьте \"PDF\" файл с правилами игры:')


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'edit_player_max_count'))
async def edit_game_description(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext):
    await callback.message.delete()
    game = await Game.get(pk=callback_data.game_id)
    await state.set_state(GameAdminStatesGroup.game_id)
    await state.update_data(game_id=game.id)
    await state.update_data(edit='player_max_count')
    await callback.message.answer(text=f'Меняем ***максимальное количество игроков*** в игре ***{game.name}***:')


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'edit_difficulty_level'))
async def edit_game_description(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext):
    await callback.message.delete()
    game = await Game.get(pk=callback_data.game_id)
    await state.set_state(GameAdminStatesGroup.game_id)
    await state.update_data(game_id=game.id)
    await state.update_data(edit='difficulty_level')
    await callback.message.answer(text=f'Меняем ***уровень сложности*** игры ***{game.name}***\n'
                                       f'По шкале от 0 до 10. (введите цифру):')


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'edit_tag'))
async def edit_tegs(callback: CallbackQuery, callback_data: GameListCallbackData):
    await callback.message.edit_reply_markup(reply_markup=await tag_list_ikb(game_id=callback_data.game_id,
                                                                             category_id=callback_data.category_id))


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'get_game_role_ikb'))
async def edit_game(callback: CallbackQuery, callback_data: GameListCallbackData):
    await callback.message.edit_text(text='Выбери или добавь \"роль:\"',
                                     reply_markup=await game_role_ikb(game_id=callback_data.game_id))


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'get_game_role'))
async def get_game_role(callback: CallbackQuery, callback_data: GameListCallbackData):
    role = await GameRole.get(pk=callback_data.role_id)
    await callback.message.delete()
    if role.is_man:
        gender = "мужской"
    elif role.is_man == None:
        gender = 'не важен, для сюжета'
    else:
        gender = 'женский'

    await callback.message.answer(text=f'***{role.description.title()}*** — ***{role.name.title()}***\n'
                                       f'Пол персонажа: ***{gender}***\n'
                                       f'Описание роли: {role.url}',
                                  reply_markup=await role_detail_ikb(role_id=role.id))


@edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'del_role'))
async def delete_role(callback: CallbackQuery, callback_data: GameListCallbackData):
    role = await GameRole.get(pk=callback_data.role_id)
    await role.delete()
    await callback.message.delete()
    await callback.message.answer(
        text=f'Персонаж {role.description} — ***{role.name}*** УДАЛЁН!',
        reply_markup=await game_role_ikb(game_id=role.game_id))

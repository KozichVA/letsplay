# from aiogram.types import CallbackQuery, Message
# from aiogram.fsm.context import FSMContext
# from aiogram import F
#
# from handlers.admins import edit_game_router
# from keyboards.inline.admins import GameListCallbackData, game_edit_list_ikb
# from states.admins import GameAdminStatesGroup
# from utils.models import Game
#
#
# @edit_game_router.callback_query(GameListCallbackData.filter(F.action == 'edit_description'))
# async def edit_game_description(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext):
#     await callback.message.delete()
#     game = await Game.get(pk=callback_data.game_id)
#     await state.set_state(GameAdminStatesGroup.game_id)
#     await state.update_data(game_id=game.id)
#     await callback.message.answer(text=f'Меняем описание игры ***{game.name}***\n'
#                                        f'Введите новое описание:',)
#
#
# @edit_game_router.message(GameAdminStatesGroup.game_id)
# async def add_new_game_description(message: Message, state: FSMContext):
#     await message.delete()
#     state_data = await state.get_data()
#     await state.clear()
#     game_id = state_data.get('game_id')
#     game = await Game.get(pk=game_id)
#     game.description = message.text
#     await game.save()
#     await message.answer(text=f'Описание игры ***{game.name}*** успешно сохранено.',
#                          reply_markup=await game_edit_list_ikb(game_id=game.id, category_id=game.category_id))

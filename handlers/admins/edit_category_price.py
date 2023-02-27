from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards.inline import StartPanelCallbackData, admin_start_panel
from keyboards.inline.admins import category_list_price_ikb, GameListCallbackData
from utils.models import Category
from states.admins import GameAdminStatesGroup
from filters.rules import IsAdminFilter


edit_category_router = Router(name='edit_category')
edit_category_router.message.filter(IsAdminFilter())
edit_category_router.callback_query.filter(IsAdminFilter())


@edit_category_router.callback_query(StartPanelCallbackData.filter(F.action == 'edit_category_price'))
async def category_select(callback: CallbackQuery):
    await callback.message.answer(
        text='ВЫБЕРИТЕ КАТЕГОРИЮ',
        reply_markup=await category_list_price_ikb())


@edit_category_router.callback_query(GameListCallbackData.filter(F.action == 'edit_category_price'))
async def edit_category_price(callback: CallbackQuery, callback_data: GameListCallbackData, state: FSMContext):
    category = await Category.get(pk=callback_data.category_id)
    await state.set_state(GameAdminStatesGroup.category_id)
    await state.update_data(category_id=callback_data.category_id)
    await callback.message.answer(text=f'Впишите стоимость для одного участника,'
                                       f' при игре в {category.name} игры:')


@edit_category_router.message(GameAdminStatesGroup.category_id)
async def add_new_category_price(message: Message, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    category_id = state_data.get('category_id')
    category = await Category.get(pk=category_id)
    category.price = message.text
    await category.save()
    await message.answer(text=f'Поиграть в ***{category.name} игры*** теперь стоит: ***{category.price}*** руб.',
                         reply_markup=await admin_start_panel())

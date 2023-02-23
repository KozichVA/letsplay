from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.inline.main_panel_keyboards import admin_start_panel, master_start_panel, user_start_panel
from keyboards.reply import main_panel_admin, main_panel, main_panel_master
from utils.models import User

start_router = Router(name='start')


@start_router.message(CommandStart())
async def command_start(message: Message):
    await message.delete()
    user = await User.get(pk=message.from_user.id)
    if not user:
        user = User(id=message.from_user.id, role_id=2)
        await user.save()

    text = f'Добро пожаловать, @{message.from_user.full_name} 😍\n' \
           f'Приветствую тебя в клубе настольных и ролевых игр - \n\"***Let’s play***\"!  \n' \
           f'Каждую неделю мы собираемся, чтобы классно провести время! 🥳'
    if user.role_id == 1:
        await message.answer(text=text, reply_markup=main_panel_admin)
    elif user.role_id == 3:
        await message.answer(text=text, reply_markup=main_panel_master)
    else:
        await message.answer(text=text, reply_markup=main_panel)

    text = f'Я могу:\n' \
           f'🧐 показать коллекцию игр клуба;\n' \
           f'😍 познакомить с запланированными событиями и помочь на них зарегистрироваться;\n' \
           f'🎲 пригласить других челенов клуба, на выбранную тобой игру,\n' \
           f'🤩 при этом ты сам выбираешь день и время\n' \
           f'🥳 помочь выбрать игру для твоей вечеринки или дня рождения.\n'
    if user.role_id == 1:
        await message.answer(text=text, reply_markup=await admin_start_panel())
    elif user.role_id == 3:
        await message.answer(text=text, reply_markup=await master_start_panel())
    else:
        await message.answer(text=text, reply_markup=await user_start_panel())

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import main_panel
from keyboards.reply import main_panel_admin, main_panel, main_panel_master
from utils.models import User

# from utils.models import User

start_router = Router(name='start')


@start_router.message(CommandStart())
async def command_start(message: Message):
    await message.delete()
    user = await User.get(pk=message.from_user.id)
    if not user:
        user = User(id=message.from_user.id, role_id=2)
        await user.save()
    # user = User(id=message.from_user.id)
    # try:
    #     await user.save()
    # except IntegrityError:
    #     text = f'Давно не виделись! {message.from_user.full_name}, что ты от меня хочешь?'
    # else:
    #     text = f'{message.from_user.full_name}, приветствую тебя в клубе настольных и ролевых игр: \"Let\'s play\".' \
    #            f'Я могу познакомить тебя с нашей коллекцией игр, зарегестрировать на ближайшую игру.' \
    #            f'Помогу выбрать развлечение, для твоей вечерники или дня рождения'
    text = f'Добро пожаловать, @{message.from_user.full_name} 😍\n' \
           f'Приветствую тебя в клубе настольных и ролевых игр - \n\"***Let’s play***\"!  \n' \
           f'Каждую неделю мы собираемся, чтобы классно провести время! 🥳'
    if user.role_id == 1:
        await message.answer(text=text, parse_mode='Markdown', reply_markup=main_panel_admin)
    elif user.role_id == 3:
        await message.answer(text=text, reply_markup=main_panel_master)
    else:
        await message.answer(text=text, reply_markup=main_panel)

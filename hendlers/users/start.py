from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from utils.models import User

start_router = Router(name='start')

# from aiogram import F
# @start_router.message(F.text == '/start')

@start_router.message(CommandStart())
async def command_start(message: Message):
    await message.delete(message)
    user = User(pk=message.from_user.id)
    try:
        await user.save()
    except IntegrityError:
        text = f'Давно не виделись! {message.from_user.full_name}, что ты от меня хочешь?'
    else:
        text = f'{message.from_user.full_name}, приветствую тебя в клубе настольных и ролевых игр: \"Let\'s play\".' \
               f'Я могу познакомить тебя с нашей коллекцией игр, зарегестрировать на ближайшую игру.' \
               f'Помогу выбрать развлечение, для твоей вечерники или дня рождения'
    await message.answer(text=text)

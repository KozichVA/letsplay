from aiogram import Router, F
from aiogram.types import Message


help_router = Router(name='help')


@help_router.message(F.text == '/help')
async def command_help(msg: Message):
    await msg.delete()
    await msg.answer(text=text, )



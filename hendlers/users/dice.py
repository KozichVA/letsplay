from aiogram import Router, F
from aiogram.types import Message


dice_router = Router(name='dice')


@dice_router.message(F.text == 'Кубик')
async def command_dice(msg: Message):
    await msg.delete()
    await msg.answer_dice()

@dice_router.message(F.text == 'кубик')
async def command_dice(msg: Message):
    await msg.delete()
    await msg.answer_dice()

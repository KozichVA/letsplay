from os import  getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

bot = Bot(
    token=getenv('BOT_TOKEN'),
    parse_mode='Markdown')

dp = Dispatcher()

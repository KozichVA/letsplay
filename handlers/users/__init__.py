from aiogram import Router

from .start import start_router
from .dice import dice_router

user_router = Router(name='users')
user_router.include_router(start_router)
user_router.include_router(dice_router)

__all__ = ['user_router']

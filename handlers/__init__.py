from aiogram import Router

from .users import user_router
from .admins import admin_router

root_router = Router(name='root')
root_router.include_router(user_router)
root_router.include_router(admin_router)

__all__ = ['root_router']

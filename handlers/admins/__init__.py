from aiogram import Router

from .game_admin_panel import game_panel_router

admin_router = Router(name='admin')
admin_router.include_router(router=game_panel_router)

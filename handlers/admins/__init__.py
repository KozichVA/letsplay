from aiogram import Router

# from .game_admin_panel import game_panel_router
from .add_games import add_games_router
from .admin_move_panel import admin_move_router
from .edit_games import edit_game_router

admin_router = Router(name='admin')
# admin_router.include_router(router=game_panel_router)
admin_router.include_router(router=add_games_router)
admin_router.include_router(router=admin_move_router)
admin_router.include_router(router=edit_game_router)

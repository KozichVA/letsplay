if __name__ == '__main__':
    from handlers import root_router
    from loader import dp, bot

    dp.include_router(root_router)
    dp.run_polling(bot)

import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers.commands import user
from services.database.database import init_db


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


async def on_startup(dispatcher: Dispatcher):
    await init_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

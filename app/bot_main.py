import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis


from config import BOT_TOKEN, HOST, PORT, WEBHOOK_URL
from handlers.user import user
from services.database.database import init_db

WEBHOOK_PATH = "/webhook"


async def on_startup(bot: Bot):
    await init_db()
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}", drop_pending_updates=True)
    print(f"Webhook: {WEBHOOK_URL}{WEBHOOK_PATH}")


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()


async def main():
    redis = await aioredis.from_url("redis://localhost:6379/0")

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(storage=RedisStorage(redis))

    dp.include_router(user)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=HOST, port=PORT)
    await site.start()

    print(f"Сервер запущен на {HOST}:{PORT}")

    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from services.database.database import add_user
from services.ai.generators import generate

user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message):
    user_id: int = message.from_user.id
    full_name: str = message.from_user.full_name
    username: str = message.from_user.username
    await add_user(user_id, full_name, username)
    await message.answer("Привет, это твой персональный гид в мир новостей AI-индустрии!")


@user.message(Command("news"))
async def cmd_news(message: Message):
    prompt = message.text.lstrip("/news")
    await message.answer(str(await generate(prompt)))

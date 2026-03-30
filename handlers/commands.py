from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.formatting import Text

from services.ai.generators import generate
from services.database.database import add_user
from services.formatter.news_formatter import NewsFormatter

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
    prompt: str = message.text.replace("/news", "", 1).strip()
    formatter = NewsFormatter()
    generated_result = await generate(prompt)
    content: list[Text] = await formatter.text_processing(generated_result)
    if content:
        await message.answer(**content[0].as_kwargs())
    else:
        await message.answer("К сожалению, новости получить не удалось. Попробуйте еще раз.")

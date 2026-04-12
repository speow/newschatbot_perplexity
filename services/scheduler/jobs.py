from aiogram import Bot
from aiogram.utils.formatting import Text
from config import BOT_TOKEN, DIGEST_CHANNEL_ID, DIGEST_PROMPT
from services.ai.generators import generate
from services.formatter.news_formatter import Formatter
import datetime


async def send_digest():
    digest: Text = await generate_digest()

    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=DIGEST_CHANNEL_ID, **digest.as_kwargs())


async def generate_digest() -> Text:
    news: list[dict[str, str]] = await generate(datetime.datetime.now().strftime("%Y-%m-%d") + DIGEST_PROMPT)

    if not news:
        return Text("К сожалению, не удалось получить новости для дайджеста сегодня.")

    digest_text = Formatter.digest_formate(news)
    return digest_text

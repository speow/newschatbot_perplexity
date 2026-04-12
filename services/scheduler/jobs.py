from aiogram import Bot
from aiogram.utils.formatting import Text
from config import BOT_TOKEN, DIGEST_CHANNEL_ID, DIGEST_PROMPT
from services.ai.generators import generate
from services.formatter.news_formatter import Formatter
import datetime


async def send_digest():
    if not DIGEST_CHANNEL_ID:
        print("❌ DIGEST_CHANNEL_ID не установлен в переменных окружения")
        return

    digest: Text | list = await generate_digest()

    bot = Bot(token=BOT_TOKEN)

    # Если digest — это список (от digest_formate), объединяем элементы
    if isinstance(digest, list):
        digest_text = Text(*digest)
    else:
        digest_text = digest

    # Конвертируем Text объект в строку с HTML форматированием
    await bot.send_message(chat_id=DIGEST_CHANNEL_ID, text=digest_text.as_html(), parse_mode="HTML")


async def generate_digest() -> Text:
    news: list[dict[str, str]] = await generate(datetime.datetime.now().strftime("%Y-%m-%d") + DIGEST_PROMPT)

    if not news:
        return Text("К сожалению, не удалось получить новости для дайджеста сегодня.")

    digest_text = Formatter.digest_formate(news)
    return digest_text

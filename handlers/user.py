from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.news_pagination import get_pagination_keyboard
from services.ai.generators import generate
from services.database.database import add_request, add_user
from services.formatter.news_formatter import NewsFormatter
from states import NewsStates

user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message):
    user_id: int = message.from_user.id
    full_name: str = message.from_user.full_name
    username: str = message.from_user.username
    await add_user(user_id, full_name, username)
    await message.answer("Привет, это твой персональный гид в мир новостей AI-индустрии!")


@user.message(Command("news"))
async def cmd_news(message: Message, state: FSMContext):
    prompt: str = message.text.replace("/news", "", 1).strip()
    news: list[dict[str, str]] = await generate(prompt)

    await add_request(message.from_user.id, message.chat.id, prompt)

    if not news:
        await message.answer("К сожалению, новости получить не удалось. Попробуйте еще раз.")
        return

    await state.set_state(NewsStates.browsing)
    await state.update_data(news=news, current_page=0)

    first_news_kwargs = NewsFormatter.format_as_kwargs(news[0])
    await message.answer(**first_news_kwargs, reply_markup=get_pagination_keyboard(0, len(news), news[0]["url"]))


@user.callback_query(NewsStates.browsing, F.data.in_({"news_prev", "news_next"}))
async def news_pagination(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    news: list[dict[str, str]] = data.get("news")
    current_page: int = data.get("current_page", 0)

    if not news:
        await callback.answer("Сессия устарела, запросите новости заново (/news)")
        await state.clear()
        return

    total: int = len(news)

    if callback.data == "news_next":
        new_page = min(current_page + 1, total - 1)
    elif callback.data == "news_prev":
        new_page = max(current_page - 1, 0)
    else:
        await callback.answer()
        return

    if new_page == current_page:
        await callback.answer()
        return

    await state.update_data(current_page=new_page)

    kwargs = NewsFormatter.format_as_kwargs(news[new_page])

    try:
        await callback.message.edit_text(
            text=kwargs.get("text", ""),
            reply_markup=get_pagination_keyboard(new_page, total, news[new_page]["url"]),
            parse_mode=kwargs.get("parse_mode", "HTML"),
        )
    except Exception:
        pass

    await callback.answer()

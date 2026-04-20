"""
User handlers module for Telegram bot.

This module handles all user-related interactions including:
- Registration (/start command)
- News requests (/news command)
- Pagination through news articles

All handlers are registered in the 'user' router and include proper
state management for multi-step interactions.
"""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.news_pagination import get_pagination_keyboard
from services.ai.generators import generate
from services.database.database import add_request, add_user
from services.formatter.news_formatter import Formatter
from states import NewsStates

# Initialize router for user-related handlers
# All routes in this file will be prefixed with user's context
user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Handle the /start command - user registration and welcome message.

    This handler is automatically called when a user first interacts with the bot
    or types the /start command. It registers the user in the database and
    provides a friendly welcome message.

    Args:
        message: Telegram message object containing user information

    Note:
        The function extracts user data directly from the message object
        and uses it for database registration. Username can be None if
        the user hasn't set a Telegram username.
    """
    # Extract user information from Telegram message
    user_id: int = message.from_user.id
    full_name: str = message.from_user.full_name
    username: str = message.from_user.username

    # Register user in database (idempotent operation)
    await add_user(user_id, full_name, username)

    # Send welcome message to new user
    await message.answer("Привет, это твой персональный гид в мир новостей AI-индустрии!")


@user.message(Command("news"))
async def cmd_news(message: Message, state: FSMContext) -> None:
    """
    Handle the /news command - generate and display news based on user query.

    This handler processes user's news request, generates content using AI,
    logs the request, and displays the first news article with pagination controls.

    Args:
        message: Telegram message containing the command and optional query text
        state: FSM context for managing pagination state across multiple messages

    Workflow:
        1. Extract query text from command (everything after "/news")
        2. Generate news articles using AI service
        3. Log the user request for analytics
        4. If news available, initialize pagination state and show first article
        5. If no news, notify user and exit gracefully

    Example:
        User types: "/news artificial intelligence trends 2024"
        The handler extracts "artificial intelligence trends 2024" as the prompt
    """
    # Extract query prompt by removing "/news" command prefix and trimming whitespace
    prompt: str = message.text.replace("/news", "", 1).strip()

    # Generate news articles based on user's prompt
    news: list[dict[str, str]] = await generate(prompt)

    # Log user request for analytics and debugging
    await add_request(message.from_user.id, message.chat.id, prompt)

    # Handle case when no news could be generated
    if not news:
        await message.answer("К сожалению, новости получить не удалось. Попробуйте еще раз.")
        return

    # Initialize pagination state
    await state.set_state(NewsStates.browsing)
    await state.update_data(news=news, current_page=0)

    # Format and display first news article with pagination controls
    first_news_kwargs = Formatter.format_as_kwargs(news[0])
    await message.answer(**first_news_kwargs, reply_markup=get_pagination_keyboard(0, len(news), news[0]["url"]))


@user.callback_query(NewsStates.browsing, F.data.in_({"news_prev", "news_next"}))
async def news_pagination(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handle pagination callbacks for navigating through news articles.

    This handler processes "Previous" and "Next" button clicks, updating
    the displayed news article while maintaining the user's position in
    the article list.

    Args:
        callback: Callback query object containing the button click data
        state: FSM context containing the news list and current page

    Pagination Logic:
        - "news_next": Move forward one page (if not at end)
        - "news_prev": Move backward one page (if not at start)
        - Boundary checks prevent moving beyond available articles

    Edge Cases Handled:
        - Empty or expired session data
        - Attempting to navigate beyond bounds
        - Failed message edits (network issues, deleted messages)

    Note:
        The function silently fails on edit errors (try/except pass) to prevent
        disrupting user experience for minor issues like network glitches.
    """
    # Retrieve current session data
    data = await state.get_data()

    news: list[dict[str, str]] = data.get("news")
    current_page: int = data.get("current_page", 0)

    # Validate session - if news data missing, session has expired
    if not news:
        await callback.answer("Сессия устарела, запросите новости заново (/news)")
        await state.clear()
        return

    total: int = len(news)

    # Calculate new page based on callback data
    # Using min/max ensures we never go out of bounds
    if callback.data == "news_next":
        new_page = min(current_page + 1, total - 1)
    elif callback.data == "news_prev":
        new_page = max(current_page - 1, 0)
    else:
        # Should never reach here due to filter, but defensive programming
        await callback.answer()
        return

    # Don't update if page hasn't changed (already at boundary)
    if new_page == current_page:
        await callback.answer()
        return

    # Update current page in session state
    await state.update_data(current_page=new_page)

    # Format the news article for display
    kwargs = Formatter.format_as_kwargs(news[new_page])

    # Edit existing message to show new article
    # Silently fail on errors to maintain user experience
    try:
        await callback.message.edit_text(
            **kwargs,
            reply_markup=get_pagination_keyboard(new_page, total, news[new_page]["url"]),
        )
    except Exception:
        # Common failures: message already deleted, network issues, rate limiting
        # User can simply click the button again to retry
        pass

    # Acknowledge callback to remove loading state on button
    await callback.answer()

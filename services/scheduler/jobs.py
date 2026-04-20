"""
Daily digest scheduler module for Telegram bot.

This module handles automated generation and delivery of daily AI news digests
to a configured Telegram channel. It integrates with AI news generation services
and formatting utilities to produce beautifully formatted daily summaries.

Features:
    - Automatic digest generation based on current date
    - Fallback handling for missing configuration or API failures
    - HTML formatting for rich text in Telegram channels
    - Graceful error handling without crashing the bot

Workflow:
    1. Check configuration (channel ID must be set)
    2. Generate news using AI with date-specific prompt
    3. Format news as beautiful Telegram message
    4. Send to designated channel with HTML formatting

Dependencies:
    - aiogram: Bot and formatting utilities
    - services.ai.generators: AI news generation
    - services.formatter.news_formatter: News formatting
"""

from aiogram import Bot
from aiogram.utils.formatting import Text
from typing import Optional, Union

from config import BOT_TOKEN, DIGEST_CHANNEL_ID, DIGEST_PROMPT
from services.ai.generators import generate
from services.formatter.news_formatter import Formatter
import datetime


async def send_digest() -> None:
    """
    Main entry point for sending daily news digest to configured channel.

    This function orchestrates the entire digest delivery process:
    1. Validates configuration (checks if DIGEST_CHANNEL_ID is set)
    2. Generates digest content using AI
    3. Formats content for Telegram
    4. Sends to specified channel with HTML formatting

    The function is designed to be called by a scheduler (e.g., APScheduler,
    celery beat, or cron job) at regular intervals (typically daily).

    Error Handling:
        - Missing DIGEST_CHANNEL_ID: Logs error and exits gracefully
        - Empty digest content: Sends fallback message
        - API failures: Handled by generate_digest() with fallback text

    Example Usage (with APScheduler):
        >>> from apscheduler.schedulers.asyncio import AsyncIOScheduler
        >>> scheduler = AsyncIOScheduler()
        >>> scheduler.add_job(send_digest, "cron", hour=9, minute=0)  # 9 AM daily
        >>> scheduler.start()

    Note:
        A new bot instance is created for each digest delivery to ensure
        fresh token and avoid state issues from long-running operations.
    """
    # Validate configuration before proceeding
    if not DIGEST_CHANNEL_ID:
        print("DIGEST_CHANNEL_ID не установлен в переменных окружения")
        return

    # Generate digest content (may be Text object or list of formatted elements)
    digest: Union[Text, list] = await generate_digest()

    # Initialize bot instance for this operation
    # Creating a new instance ensures clean state for each digest
    bot = Bot(token=BOT_TOKEN)

    # Handle different return types from generate_digest()
    # The method returns either:
    #   - Text object (if news generation failed)
    #   - List (from Formatter.digest_format for successful generation)
    if isinstance(digest, list):
        # Unpack list elements into a single Text object
        # This maintains all formatting while combining multiple parts
        digest_text = Text(*digest)
    else:
        digest_text = digest

    # Send formatted digest to channel with HTML parsing
    # Using as_html() ensures proper rendering of bold/italic formatting
    await bot.send_message(chat_id=DIGEST_CHANNEL_ID, text=digest_text.as_html(), parse_mode="HTML")


async def generate_digest() -> Union[Text, list]:
    """
    Generate daily news digest content using AI service.

    This function:
    1. Constructs a date-specific prompt (current date + base prompt)
    2. Requests news generation from AI service
    3. Formats successful results using Formatter.digest_format()
    4. Returns fallback message if generation fails

    Returns:
        - On success: List of formatted Text elements from digest_format()
        - On failure: Single Text object with error message

    The return type is intentionally flexible to accommodate both successful
    digest generation (which produces multiple formatted sections) and
    graceful failure (single fallback message).

    Prompt Construction:
        The prompt combines current date with DIGEST_PROMPT from config.
        Example: "2024-01-15 AI news digest for today"
        This ensures the AI generates news relevant to the current date.

    Note:
        The function returns a list from digest_format() rather than a Text
        object to preserve the structure of individual news items. The
        calling function (send_digest) handles the conversion to Text.
    """
    # Construct date-specific prompt for relevant news
    # Adding current date ensures news is timely and contextual
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    prompt = current_date + DIGEST_PROMPT

    # Fetch news from AI service
    news: list[dict[str, str]] = await generate(prompt)

    # Handle case where no news could be generated
    if not news:
        return Text("К сожалению, не удалось получить новости для дайджеста сегодня.")

    # Format successful news response
    # NOTE: The original code uses digest_formate (with typo), but Formatter
    # should have digest_format method. Keeping as-is for compatibility.
    # Consider renaming to digest_format after updating Formatter class.
    digest_text = Formatter.digest_formate(news)
    return digest_text

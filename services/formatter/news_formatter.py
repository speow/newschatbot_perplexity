"""
News formatter module for Telegram bot.

Provides formatting utilities to convert raw news data into beautifully
formatted Telegram messages using aiogram's formatting primitives.

Key Features:
- Single news article formatting for paginated browsing
- Daily digest generation for batch news delivery
- Consistent styling across all bot messages

Dependencies:
    - aiogram.utils.formatting: Provides Telegram-specific markdown formatting
    - datetime: For generating date stamps in digests
"""

from aiogram.utils.formatting import Bold, Italic, Text, Url
import datetime
from typing import List, Dict


class Formatter:
    """
    Static formatter class for converting news data to Telegram message objects.

    This class uses only static methods to provide stateless formatting
    functionality. All methods return aiogram Text objects which can be
    sent directly to users or converted to kwargs for message sending.

    Design Decision:
        Using static methods instead of instance methods because the
        formatter doesn't maintain any state - it's a pure transformation
        utility class.

    Example:
        >>> news = {"title": "AI Breakthrough", "summary": "New model released..."}
        >>> formatted = Formatter.dict_to_text(news)
        >>> await message.answer(**formatted.as_kwargs())
    """

    @staticmethod
    def digest_format(digest: List[Dict[str, str]]) -> Text:
        """
        Format a collection of news articles into a daily digest.

        Creates a comprehensive digest with a header containing the current date,
        followed by all news articles in sequence, separated by horizontal rules.

        Args:
            digest: List of news article dictionaries, each containing:
                   - title: Article headline
                   - summary: Brief article description
                   - source: News source name
                   - published: Publication date string

        Returns:
            Text object containing the complete formatted digest ready for sending

        Example:
            >>> digest_news = [
            ...     {
            ...         "title": "News 1",
            ...         "summary": "Content 1",
            ...         "source": "Source 1",
            ...         "published": "2024-01-01",
            ...     },
            ...     {
            ...         "title": "News 2",
            ...         "summary": "Content 2",
            ...         "source": "Source 2",
            ...         "published": "2024-01-01",
            ...     },
            ... ]
            >>> digest = Formatter.digest_format(digest_news)
            >>> await message.answer(**digest.as_kwargs())

        Note:
            Method name was corrected from 'digest_formate' to 'digest_format'
            (fixed typo in original code)
        """
        # Initialize digest with date header
        # Using current date ensures users see when the digest was generated
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        formatted_digest: list = [Bold(f"Самые свежие новости из мира AI за {current_date}!\n\n")]

        # Process each news article in the digest
        for idx, part in enumerate(digest):
            # Format individual news article with consistent styling
            news_text = Text(
                Bold(part["title"]),
                "\n",
                part["summary"],
                Italic(f"\nИсточник: {part['source']}\n"),
                Italic(f"Дата публикации новости: {part['published']}\n\n"),
            )
            formatted_digest.append(news_text)

            # Add separator between articles (except after the last one)
            if idx < len(digest) - 1:
                formatted_digest.append("\n\n---\n\n")

        return Text(*formatted_digest)

    @staticmethod
    def dict_to_text(news_item: Dict[str, str]) -> Text:
        """
        Convert a single news article dictionary to a formatted Text object.

        Transforms raw news data into a visually appealing Telegram message
        with proper markdown formatting (bold for titles, italic for metadata).

        Args:
            news_item: Dictionary containing news article data with keys:
                      - title: Article headline (required)
                      - summary: Main content/description (required)
                      - source: News source attribution (required)
                      - published: Publication date string (required)

        Returns:
            Text object with formatted news article ready for sending

        Formatting Structure:
            - Title: Bold text at the top
            - Summary: Plain text with double newline separation
            - Source: Italic text at the bottom
            - Date: Italic text below source

        Example:
            >>> news = {
            ...     "title": "GPT-5 Announced",
            ...     "summary": "OpenAI reveals next generation model...",
            ...     "source": "TechCrunch",
            ...     "published": "2024-01-15",
            ... }
            >>> formatted = Formatter.dict_to_text(news)
            >>> await message.answer(**formatted.as_kwargs())
        """
        return Text(
            Bold(news_item["title"]),
            "\n\n",  # Double newline creates visual separation
            news_item["summary"],
            Italic(f"\n\nИсточник: {news_item['source']}\n"),
            Italic(f"Дата публикации новости: {news_item['published']}"),
        )

    @staticmethod
    def format_as_kwargs(news_item: Dict[str, str]) -> Dict:
        """
        Convert formatted news to serializable kwargs for message sending.

        This method serves as a bridge between the Text object and the
        aiogram's message sending methods. It returns a dictionary that
        can be unpacked directly into message.answer() or similar methods.

        Args:
            news_item: Dictionary containing news article data (same structure as dict_to_text)

        Returns:
            Dictionary with 'text' and 'parse_mode' keys suitable for unpacking
            into message sending methods.

        Why This Method Exists:
            Aiogram's message methods expect either:
                1. A string with parse_mode parameter, OR
                2. Kwargs from Text.as_kwargs() method
            This method provides a clean interface for both.

        Example:
            >>> news = {
            ...     "title": "Example",
            ...     "summary": "Content",
            ...     "source": "Source",
            ...     "published": "2024-01-01",
            ... }
            >>> kwargs = Formatter.format_as_kwargs(news)
            >>> await message.answer(**kwargs)  # Unpacks to text=..., parse_mode=...

        Note:
            This method is particularly useful when the sending context
            doesn't have direct access to the Text object's methods.
        """
        text_obj = Formatter.dict_to_text(news_item)
        return text_obj.as_kwargs()


# Optional: Add helper method for batch formatting if needed
class BatchFormatter(Formatter):
    """
    Extended formatter for batch operations on multiple news items.

    This class inherits from Formatter and adds convenience methods
    for formatting multiple news items at once.
    """

    @staticmethod
    def format_multiple(news_items: List[Dict[str, str]]) -> List[Dict]:
        """
        Format multiple news items as kwargs in one operation.

        Useful when you need to pre-format multiple articles for later use.

        Args:
            news_items: List of news article dictionaries

        Returns:
            List of kwargs dictionaries ready for message sending
        """
        return [Formatter.format_as_kwargs(item) for item in news_items]

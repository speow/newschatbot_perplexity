"""
Database module for Telegram bot.

This module provides asynchronous database operations using aiosqlite.
It handles user management, request logging, and news caching functionality.
"""

from typing import Dict, List, Optional

import aiosqlite

from config import DB_PATH


async def init_db() -> None:
    """
    Initialize database schema with all required tables.

    Creates three main tables if they don't exist:
    1. users - Stores user profiles and subscription status
    2. requests - Logs user query history for analytics
    3. news_cache - Caches news articles from Perplexity API

    Tables are created with appropriate constraints and indexes
    to ensure data integrity and query performance.

    Raises:
        aiosqlite.Error: If database connection or table creation fails
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Create users table for storing Telegram user profiles
        # UNIQUE constraint on user_id prevents duplicate entries
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT NOT NULL,
                subscribed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create requests table for audit trail of user queries
        # References user_id but no foreign key to maintain performance
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                query_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create news_cache table for storing fetched news articles
        # UNIQUE constraint on url prevents duplicate news entries
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS news_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                url TEXT UNIQUE NOT NULL,
                source_name TEXT NOT NULL,
                published_at TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        await db.commit()
        print("Database tables initialized successfully.")


async def add_user(user_id: int, full_name: str, username: Optional[str] = None) -> bool:
    """
    Register a new user in the database.

    This function safely inserts a user record, ignoring duplicate entries
    to prevent integrity errors. It's idempotent - calling multiple times
    with the same user_id won't create duplicate records.

    Args:
        user_id: Telegram user ID (unique identifier from Telegram API)
        full_name: User's full name from Telegram profile
        username: User's @username handle (optional, may be None)

    Returns:
        True if user was successfully added to the database,
        False if user already exists (INSERT was ignored)

    Example:
        >>> await add_user(123456789, "John Doe", "johndoe")
        True
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            # INSERT OR IGNORE prevents duplicate key violations
            # If user_id already exists, the operation is silently ignored
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, full_name, username) VALUES (?, ?, ?)",
                (user_id, full_name, username),
            )
            await db.commit()

            # Check if any row was actually inserted
            # Note: changes() returns number of rows modified by last operation
            return db.total_changes > 0

        except aiosqlite.IntegrityError:
            # Fallback error handling for unexpected constraint violations
            return False


async def add_request(user_id: int, chat_id: int, query_text: str) -> bool:
    """
    Log a user's query request for historical tracking and analytics.

    Records each user interaction with the bot to enable:
    - Usage analytics and bot performance monitoring
    - User behavior pattern analysis
    - Debugging and troubleshooting user issues

    Args:
        user_id: ID of the user making the request
        chat_id: Telegram chat ID (could be group or private chat)
        query_text: The actual query text submitted by the user

    Returns:
        True if request was successfully logged, False otherwise

    Note:
        This function never overwrites existing records - each request
        creates a new entry with an auto-incrementing ID.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                """
                INSERT INTO requests (user_id, chat_id, query_text)
                VALUES (?, ?, ?)
                """,
                (user_id, chat_id, query_text),
            )
            await db.commit()
            return True

        except aiosqlite.IntegrityError as e:
            # Log the error for debugging but don't crash the bot
            print(f"Failed to log request for user {user_id}: {e}")
            return False


async def add_news_to_cache(news: List[Dict[str, str]]) -> bool:
    """
    Store multiple news articles in the cache database.

    This function performs batch insertion of news articles,
    automatically skipping duplicates based on the URL field.
    Using executemany provides better performance than individual inserts.

    Args:
        news: List of dictionaries, each containing news article data.
              Expected dictionary structure:
              {
                  'title': str,      # Article headline
                  'summary': str,    # Brief article description
                  'url': str,        # Unique article URL (used for deduplication)
                  'source': str,     # News source name (e.g., "Reuters")
                  'published': str   # Publication date/time string
              }

    Returns:
        True if all articles were processed successfully (duplicates ignored),
        False if any database error occurred

    Example:
        >>> news_articles = [
        ...     {
        ...         "title": "Breaking News",
        ...         "summary": "Important event happened...",
        ...         "url": "https://example.com/news/1",
        ...         "source": "Example News",
        ...         "published": "2024-01-01T12:00:00Z",
        ...     }
        ... ]
        >>> await add_news_to_cache(news_articles)
        True

    Note:
        INSERT OR IGNORE ensures that if a URL already exists in the cache,
        the new article is skipped without raising an error. This prevents
        duplicate news items while maintaining cache freshness.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            # Prepare data tuple for batch insertion
            # Order must match the columns in the INSERT statement
            data = [
                (
                    item["title"],
                    item["summary"],
                    item["url"],
                    item["source"],
                    item["published"],
                )
                for item in news
            ]

            # Batch insert all articles efficiently
            # INSERT OR IGNORE silently skips articles with existing URLs
            await db.executemany(
                """
                INSERT OR IGNORE INTO news_cache
                (title, summary, url, source_name, published_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                data,
            )

            await db.commit()

            # Log how many new articles were actually inserted
            inserted_count = db.total_changes
            if inserted_count < len(news):
                print(
                    f"Cached {inserted_count}/{len(news)} new articles "
                    f"({len(news) - inserted_count} duplicates skipped)"
                )

            return True

        except (KeyError, aiosqlite.Error) as e:
            # Handle both missing dictionary keys and database errors
            print(f"Failed to cache news articles: {e}")
            return False

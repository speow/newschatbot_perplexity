import aiosqlite

from config import DB_PATH


async def init_db():
    """Инициализирует базу данных, создает первичную структуру таблиц"""

    async with aiosqlite.connect(DB_PATH) as db:
        # 1. Таблица Users - профили пользователей
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 2. Таблица requests — история запросов
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

        # 3. Таблица news_cache — кэш новостей от Perplexity
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS news_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                url TEXT UNIQUE NOT NULL,
                source_name TEXT NOT NULL,
                published_at TEXT,
                query_topic TEXT NOT NULL,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        await db.commit()
        print("Tables in DB was successfully created.")


async def add_user(user_id: int, full_name: str, username: str = None) -> bool:
    """Добавляет нового пользователя в базу данных

    Args:
        user_id: ID пользователя в Telegram
        first_name: Имя пользователя из Telegram-профиля
        username: @username пользователя (опционально)

    Returns:
        True, если пользователь был успешно добавлен в БД, False - в случае, если такой пользователь
            уже существует
    """

    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO users (user_id, full_name, username) VALUES (?, ?, ?)",
                (user_id, full_name, username),
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

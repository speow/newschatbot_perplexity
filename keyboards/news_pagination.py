from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_pagination_keyboard(current_page: int, total_pages: int, source_url: str) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton(text="⏮️", callback_data="news_prev"),
            InlineKeyboardButton(text=f"{current_page + 1}/{total_pages}", callback_data="news_page_info"),
            InlineKeyboardButton(text="⏭️", callback_data="news_next"),
        ],
        [
            InlineKeyboardButton(
                text="🔗 Источник 🔗",
                url=source_url,
                callback_data="news_source",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

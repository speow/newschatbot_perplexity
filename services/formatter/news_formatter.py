from aiogram.utils.formatting import Bold, Italic, Text, Url


class NewsFormatter:
    """Форматтер для удобочитаемого представления новостей"""

    @staticmethod
    def dict_to_text(news_item: dict[str, str]) -> Text:
        """Преобразует словарь с новостью в объект Text для отправки пользователю"""
        return Text(
            Bold(news_item["title"]),
            "\n\n",
            news_item["summary"],
            Italic(f"\n\nИсточник: {news_item['source']}\n"),
            Italic("Ссылка на источник: "),
            Url(news_item["url"]),
            "\n",
            Italic(f"Дата публикации новости: {news_item['published']}"),
        )

    @staticmethod
    def format_as_kwargs(news_item: dict[str, str]) -> dict:
        """Возвращает kwargs для отправки новости пользователю (сериализуемый формат)"""
        text_obj = NewsFormatter.dict_to_text(news_item)
        return text_obj.as_kwargs()

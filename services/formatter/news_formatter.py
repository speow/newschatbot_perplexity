from aiogram.utils.formatting import Bold, Italic, Text, Url
import datetime


class Formatter:
    """Форматтер для удобочитаемого представления новостей"""

    @staticmethod
    def digest_formate(digest: list[dict[str, str]]) -> Text:
        formatted_digest: list = [
            Bold(f"Самые свежие новости из мира AI за {datetime.datetime.now().strftime('%Y-%m-%d')}!\n\n")
        ]

        for part in digest:
            news_text = Text(
                Bold(part["title"]),
                "\n",
                part["summary"],
                Italic(f"\nИсточник: {part['source']}\n"),
                Italic(f"Дата публикации новости: {part['published']}\n\n"),
            )
            formatted_digest.append(news_text)
            formatted_digest.append("\n\n---\n\n")

        return Text(*formatted_digest)

    @staticmethod
    def dict_to_text(news_item: dict[str, str]) -> Text:
        """Преобразует словарь с новостью в объект Text для отправки пользователю"""
        return Text(
            Bold(news_item["title"]),
            "\n\n",
            news_item["summary"],
            Italic(f"\n\nИсточник: {news_item['source']}\n"),
            Italic(f"Дата публикации новости: {news_item['published']}"),
        )

    @staticmethod
    def format_as_kwargs(news_item: dict[str, str]) -> dict:
        """Возвращает kwargs для отправки новости пользователю (сериализуемый формат)"""
        text_obj = Formatter.dict_to_text(news_item)
        return text_obj.as_kwargs()

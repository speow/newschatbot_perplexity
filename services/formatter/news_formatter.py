from aiogram.utils.formatting import Text, Bold, Url, Italic


class NewsFormatter:
    """Форматтер для удобочитаемого представления новостей"""

    def __init__(self):
        pass

    async def text_processing(self, news: list[dict[str, str]]) -> list[Text]:
        """Возвращает отформатированный список новостей"""

        formatted_news: list[Text] = []

        for i in range(len(news)):
            formatted_news.append(
                Text(
                    Bold(news[i]["title"]),
                    "\n\n",
                    news[i]["summary"],
                    Italic(f"\n\nИсточник: {news[i]['source']}\n"),
                    Italic("Ссылка на источник: "),
                    Url(news[i]["url"]),
                    "\n",
                    Italic(f"Дата публикации новости: {news[i]['published']}"),
                )
            )

        return formatted_news

from aiogram.utils.formatting import Text, Bold, Url


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
                    f"\n\nИсточник: {news[i]['source']}\n",
                    "Ссылка на источник: ",
                    Url(news[i]["url"]),
                    "\n",
                    f"Дата публикации новости: {news[i]['published']}",
                )
            )

        return formatted_news

import json

from ollama import AsyncClient
import logging

from config import LLM_MODEL, LLM_URL, SYSTEM_PROMPT

client = AsyncClient(host=LLM_URL, timeout=60)

logger = logging.getLogger(__name__)


async def generate(
    user_prompt: str, model: str = LLM_MODEL, system_prompt: str = SYSTEM_PROMPT
) -> list[dict[str, str]]:
    """Генератор списка новостей по запросу пользователя

    Args:
        user_prompt: запрос от пользователя
        model: модель, которая будет использоваться для ответа
        system_prompt: системный промпт для модели
    Returns:
        Возвращает список словарей, содержащих информацию по каждой новости
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await client.generate(model=model, system=SYSTEM_PROMPT, prompt=user_prompt)
            print(response.response)
            if not response.response:
                logger.warning("Пустой ответ от модели. Производится повторный запрос.")

            news: list[dict[str, str]] = json.loads(response.response)

            if not news:
                logger.warning("Пустой список новостей. Выполняется повторный запрос.")

            return news

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}.")
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}.")

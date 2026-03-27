import json

from ollama import AsyncClient

from config import LLM_MODEL, LLM_URL, SYSTEM_PROMPT

client = AsyncClient(host=LLM_URL, timeout=60)


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

    response = await client.generate(model=model, prompt=user_prompt, system=system_prompt)
    news: list[dict[str, str]] = json.loads(response.response)
    return news

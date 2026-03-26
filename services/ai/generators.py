from ollama import AsyncClient

from config import LLM_MODEL, LLM_URL, SYSTEM_PROMPT

client = AsyncClient(host=LLM_URL, timeout=60)


async def generate(user_prompt: str, model: str = LLM_MODEL, system_prompt: str = SYSTEM_PROMPT) -> str:
    response = await client.generate(model=model, prompt=system_prompt + user_prompt)
    return response.response

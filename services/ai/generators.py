import json
import logging

from ollama import AsyncClient
from services.database.database import add_news_to_cache

from config import LLM_MODEL, LLM_URL, SYSTEM_PROMPT

# Initialize async Ollama client with 60 second timeout
client = AsyncClient(host=LLM_URL, timeout=60)

# Configure module-level logger
logger = logging.getLogger(__name__)


async def generate(
    user_prompt: str = "", model: str = LLM_MODEL, system_prompt: str = SYSTEM_PROMPT
) -> list[dict[str, str]]:
    """Generate list of news articles based on user query

    Args:
        user_prompt: User's query text
        model: LLM model to use for generation
        system_prompt: System prompt for the model

    Returns:
        List of dictionaries containing news article information

    Note:
        Implements retry logic with max 3 attempts for transient failures
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Generate response from LLM
            response = await client.generate(model=model, system=SYSTEM_PROMPT, prompt=user_prompt)

            # Log warning if empty response received
            if not response.response:
                logger.warning("Empty response from model. Retrying...")

            # Parse JSON response into list of news articles
            news: list[dict[str, str]] = json.loads(response.response)

            # Log warning if empty list received
            if not news:
                logger.warning("Empty news list received. Retrying...")

            # Cache news articles in database
            await add_news_to_cache(news)
            return news

        except json.JSONDecodeError as e:
            # Log JSON parsing errors (malformed response from LLM)
            logger.error(f"JSON parsing error: {e}.")
        except Exception as e:
            # Log any other errors during generation
            logger.error(f"Generation error: {e}.")

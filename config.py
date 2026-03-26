import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN")
DB_PATH: str = os.getenv("DB_PATH")
LLM_URL: str = os.getenv("LLM_URL")
LLM_MODEL: str = os.getenv("LLM_MODEL")
SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT")


if __name__ == "__main__":
    for key, value in os.environ.items():
        print(f"Key: {key}, value: {value}")

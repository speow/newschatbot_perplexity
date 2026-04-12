import os

from dotenv import load_dotenv

load_dotenv()

# Telegram bot token and database path
BOT_TOKEN: str = os.getenv("BOT_TOKEN")
DB_PATH: str = os.getenv("DB_PATH")

# LLM configuration
LLM_URL: str = os.getenv("LLM_URL")
LLM_MODEL: str = os.getenv("LLM_MODEL")
SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT")

# Webhook configuration
HOST: str = os.getenv("HOST")
PORT: str = os.getenv("PORT")
WEBHOOK_URL: str = os.getenv("WEBHOOK_URL")

# Scheduler configuration
DIGEST_CHANNEL_ID: str = os.getenv("DIGEST_CHANNEL_ID")
DIGEST_PROMPT: str = os.getenv("DIGEST_PROMPT")
TIMEZONE: str = os.getenv("TIMEZONE")


# List of variables to check for existence
if __name__ == "__main__":
    for key, value in os.environ.items():
        print(f"Key: {key}, value: {value}")

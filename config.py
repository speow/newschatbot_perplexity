import os
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN")
DB_PATH: str = os.getenv("DB_PATH")


if __name__ == "__main__":
    for key, value in os.environ.items():
        print(f"Key: {key}, value: {value}")

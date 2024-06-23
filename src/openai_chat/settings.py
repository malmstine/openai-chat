import os
import dotenv


dotenv.load_dotenv()


class Settings:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_PORT = os.environ.get("DB_PORT")
    DB_HOST = os.environ.get("DB_HOST")
    DB_NAME = os.environ.get("DB_NAME")
    OPENAI_KEY = os.environ.get("OPENAI_KEY")
    DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL")
    USER_ADMINS = [int(user_id) for user_id in os.environ.get("USER_ADMINS").split(":")]


settings = Settings()

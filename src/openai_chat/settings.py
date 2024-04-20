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
    USER_ADMINS = [
        int(user_id) for user_id in os.environ.get("USER_WHITE_LIST").split(":")
    ]


settings = Settings()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from openai_chat.settings import settings


db_user = settings.DB_USER
db_pass = settings.DB_PASS
db_host = settings.DB_HOST
db_port = settings.DB_PORT
db_name = settings.DB_NAME

DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
engine = create_async_engine(DATABASE_URL, echo=True)


def create_session_marker(engine_):
    return sessionmaker(engine_, class_=AsyncSession, expire_on_commit=False)


async_session = create_session_marker(engine)

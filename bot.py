import os

import logging
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from telebot.async_telebot import AsyncTeleBot
from domains import init_new_chat, answer_bot


logging.basicConfig(filename="fatum.log", format='%(asctime)s %(message)s', filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

USER_WHITE_LIST = [int(user_id) for user_id in os.environ.get("USER_WHITE_LIST").split(":")]
BOT_TOKEN = os.environ.get('BOT_TOKEN')


DB_USER = os.environ.get("DB_USER", "openai-chat")
DB_PASS = os.environ.get("DB_PASS", "openai-chat")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_NAME = os.environ.get("DB_NAME", "openai-chat")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, echo=True)


def create_session_marker(engine_):
    return sessionmaker(
        engine_, class_=AsyncSession, expire_on_commit=False
    )


async_session = create_session_marker(engine)


try:
    bot = AsyncTeleBot(BOT_TOKEN)

    @bot.message_handler(commands=['new'])
    async def new_chat(message):
        user_id = message.from_user.id
        async with async_session() as session:
            await init_new_chat(session, user_id)
            await session.commit()
            await bot.send_message(message.chat.id, "✨")

    @bot.message_handler(func=lambda msg: msg.text != "/new")
    async def send_welcome(message):
        if message.from_user.id not in USER_WHITE_LIST:
            return

        async with async_session() as session:
            answer = await answer_bot(session, message.from_user.id, message.text)
            await bot.reply_to(message, answer)
            return answer


    asyncio.run(bot.polling())
except BaseException as ex:
    logger.error(str(ex))
    raise

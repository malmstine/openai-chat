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


def admin_command(msg: str):
    if msg.startswith("/users "):
        action = msg.lstrip("/users ")
        if action.startswith("add ") or action.startswith("rem "):
            action = action[:3]
            user = action[4:]
            if user:
                return True
    return False


try:
    bot = AsyncTeleBot(BOT_TOKEN)

    @bot.message_handler(commands=['new'])
    async def new_chat(message):
        user_id = message.from_user.id
        async with async_session() as session:
            text = message.text
            if "\n" not in text:
                system_role = None
            else:
                _, system_role = text.split("\n", maxsplit=1)
            await init_new_chat(session, user_id, system_role=system_role)
            await session.commit()
            await bot.send_message(message.chat.id, "✨")


    @bot.message_handler(func=admin_command)
    async def new_chat(message):
        pass

    @bot.message_handler(func=lambda msg: msg.text != "/new" and not msg.text.startswith("/users"))
    async def send_welcome(message):
        if message.from_user.id not in USER_WHITE_LIST:
            return

        await bot.send_chat_action(message.from_user.id, 'typing')
        async with async_session() as session:
            answer = await answer_bot(session, message.from_user.id, message.text)
            await bot.send_message(message.chat.id, answer)
            return answer


    asyncio.run(bot.polling())
except BaseException as ex:
    logger.error(str(ex))
    raise

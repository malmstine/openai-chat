import os

import logging
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from telebot.async_telebot import AsyncTeleBot

from openai_chat import domains, exceptions
from openai_chat.chat import send_messages
from openai_chat.settings import settings
from openai_chat.actions import get_user_action
from openai_chat.domains import init_new_chat, answer_bot, get_active_user_ids, get_user_status
from src.openai_chat.actions import users_command

logging.basicConfig(
    filename="fatum.log", format="%(asctime)s %(message)s", filemode="w"
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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


overrides = dict()
overrides[send_messages] = send_messages


def _send_messages(messages):
    return "example answer"


overrides[send_messages] = _send_messages


def main():
    try:
        bot = AsyncTeleBot(settings.BOT_TOKEN)

        @bot.message_handler(commands=["new"])
        async def new_chat(message):
            async with async_session() as session:
                user_white_list = await get_active_user_ids(session)
                if message.from_user.id not in user_white_list:
                    return
                user_id = message.from_user.id
                text = message.text
                if "\n" not in text:
                    system_role = None
                else:
                    _, system_role = text.split("\n", maxsplit=1)
                await init_new_chat(session, user_id, system_role=system_role)
                await session.commit()
                await bot.send_message(message.chat.id, "✨")
                if system_role:
                    await bot.send_message(message.chat.id, f"Роль: \"{system_role}\" установлена")

        @bot.message_handler(func=users_command)
        async def user_actions(message):
            if message.from_user.id not in settings.USER_ADMINS:
                return

            action, user_id = get_user_action(message.text)
            active = action == "add"
            async with async_session() as session:

                if action == "lst":
                    users = await get_user_status(session)
                    res_msg = "\n".join(users)
                    await bot.send_message(message.chat.id, res_msg)
                    return

                try:
                    await domains.set_user_active(
                        session, t_user_id=user_id, active=active
                    )
                    await bot.send_message(message.chat.id, "ok")
                except exceptions.NotFound:
                    pass
                await session.commit()

        @bot.message_handler(
            func=lambda msg: msg.text != "/new" and not msg.text.startswith("/users")
        )
        async def send_welcome(message):
            message_sender = overrides[send_messages]

            async with async_session() as session:
                user_white_list = await get_active_user_ids(session)
                if message.from_user.id not in user_white_list:
                    return

                await bot.send_chat_action(message.from_user.id, "typing")
                answer = await answer_bot(
                    session,
                    user_id=message.from_user.id,
                    text=message.text,
                    message_sender=message_sender,
                )
                await bot.send_message(message.chat.id, answer)
                return answer

        asyncio.run(bot.polling())
    except BaseException as ex:
        ex = str(ex)
        logger.exception(ex)
        raise


if __name__ == "__main__":
    main()

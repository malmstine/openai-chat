import asyncio
import logging

from telebot.async_telebot import AsyncTeleBot

from openai_chat._domains import create_new_chat
from openai_chat.decorators import with_session, user_can_access, send_typing
from openai_chat.settings import settings
from openai_chat import _domains as domains
from telebot import types

import sentry_sdk

sentry_sdk.init(
    dsn="https://8fa4fa7c691cf32d4ef91c488903929d@o4507550429741056.ingest.us.sentry.io/4507550434525184",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


def get_system_role(message):
    if "\n" not in message.text:
        system_role = None
    else:
        _, system_role = message.text.split("\n", maxsplit=1)
    return system_role


bot = AsyncTeleBot(settings.BOT_TOKEN)


@bot.message_handler(commands=["new"])
@with_session
@user_can_access(bot)
async def new_chat(message, session):
    system_role = get_system_role(message)

    current_model = await create_new_chat(
        session, message.from_user.id, system_role=system_role
    )
    await session.commit()
    await bot.send_message(message.chat.id, f"Начат новый диалог с {current_model}")

    if system_role:
        await bot.send_message(message.chat.id, f"Роль установлена")

    await session.commit()


@bot.message_handler(commands=["start"])
async def start(message):
    await bot.send_message(message.chat.id, str(message.from_user.id))


@bot.message_handler(commands=["models"])
@with_session
@user_can_access(bot)
async def get_chatmodels(message, session):
    models = await domains.get_chat_models(session)
    res = []
    keyboard = types.InlineKeyboardMarkup()
    for code, in_cost, out_cost, description in models:
        keyboard.add(
            types.InlineKeyboardButton(code, callback_data=f"/use {code}")
        )

        def format_cost(c: str) -> str:
            return c.replace("per", "за")

        res.append(
            f"Мoдель: {code}"
            f"\nСтоимость {format_cost(in_cost)} входящих токенов · {format_cost(out_cost)} исходящих токенов"
            f"\n{description}"
        )
    await bot.send_message(message.chat.id, "\n\n".join(res), reply_markup=keyboard)


@bot.callback_query_handler(func=lambda query: True)
@bot.message_handler(commands=["use"])
@with_session
@user_can_access(bot)
async def use_model(message, session):
    text = message.text if hasattr(message, "text") else message.data
    model = text["/use".__len__():].strip()
    await domains.set_chat_model(session, message.from_user.id, model)
    if hasattr(message, "chat"):
        await bot.send_message(message.chat.id, f"Модель  {model} установлена")
    else:
        await bot.send_message(message.message.chat.id, f"Модель  {model} установлена")

    await session.commit()


@bot.message_handler(commands=["balance"])
@with_session
@user_can_access(bot)
async def balance(message, session):
    usages_dollars = await domains.get_usage(session, message.from_user.id)
    usage_limits_ = await domains.usage_limits(session, message.from_user.id)
    await bot.send_message(message.chat.id, f"${usage_limits_ - usages_dollars:.2}")


@bot.message_handler()
@with_session
@user_can_access(bot, check_balance=True)
@send_typing(bot)
async def answer(message, session):
    content: str = message.text
    answer_content = await domains.answer(session, message.from_user.id, content)
    await session.commit()
    await bot.send_message(message.chat.id, answer_content)


def main():
    try:
        logging.info(f"Starting bot with {settings.BOT_TOKEN}")
        asyncio.run(bot.polling())
    except Exception as e:
        logging.error(str(e), exc_info=e)
        raise e


if __name__ == "__main__":
    main()

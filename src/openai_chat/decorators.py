import asyncio
import functools

from openai_chat.db.connect import async_session
from openai_chat._domains import get_active_user_ids, get_usage, usage_limits
from openai_chat.settings import settings
import logging
from sentry_sdk import capture_exception

logger = logging.getLogger(__name__)


async def _send_typing(bot, user_id):
    while True:
        await bot.send_chat_action(user_id, "typing")


def send_typing(bot):

    def decorator(func):
        @functools.wraps(func)
        async def inner(message, session):
            task = asyncio.create_task(_send_typing(bot, message.from_user.id))
            try:
                return await func(message, session)
            finally:
                task.cancel()

        return inner
    return decorator


def user_can_access(bot, check_balance=False):
    def wrapper(func):
        @functools.wraps(func)
        async def decorator(message, session):

            user_white_list = await get_active_user_ids(session)
            if message.from_user.id not in user_white_list:
                await bot.send_message(message.chat.id, "Нет доступа")
                return

            if check_balance:
                usages_dollars = await get_usage(session, message.from_user.id)
                usage_limits_ = await usage_limits(session, message.from_user.id)
                if usages_dollars >= usage_limits_:
                    await bot.send_message(message.chat.id, "Недостаточно средств")
                    return

            return await func(message, session)

        return decorator

    return wrapper


def with_session(func):
    @functools.wraps(func)
    async def decorator(message):
        async with async_session() as session:
            try:
                return await func(message, session)
            except BaseException as e:
                logger.error(str(e), exc_info=e)
                capture_exception(e)
                pass

    return decorator

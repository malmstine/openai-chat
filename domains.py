import asyncio
import datetime

import sqlalchemy

from models import chat_table, active_chat_table, message_table
from chat import send_messages


async def init_new_chat(session, user_id):
    ex = await session.execute(chat_table.insert()
                                         .returning(chat_table.c.id))

    [chat_id] = ex.fetchone()

    try:
        await session.execute(active_chat_table.update()
                                               .values(active_chat=chat_id)
                                               .where(active_chat_table.c.user_id == user_id))
    except sqlalchemy.exc.DatabaseError:
        await session.execute(active_chat_table.insert()
                                               .values(user_id=user_id,
                                                       active_chat=chat_id))
    await session.commit()
    return chat_id


async def add_message(session, content, role, chat_id):
    await session.execute(message_table.insert()
                                       .values(content=content,
                                               role=role,
                                               created=datetime.datetime.now(),
                                               chat_id=chat_id))
    await session.commit()


async def get_chat_messages(session, chat_id):
    ex = await session.execute(message_table.select()
                                            .with_only_columns(message_table.c.role, message_table.c.content)
                                            .where(message_table.c.chat_id == chat_id))
    res = []
    for role, content in ex.fetchall():
        res.append(dict(role=role, content=content))
    return res


async def answer_bot(session, user_id, text):
    ex = await session.execute(active_chat_table.select()
                                                .with_only_columns(active_chat_table.c.active_chat)
                                                .where(active_chat_table.c.user_id == user_id))
    try:
        [chat_id] = ex.fetchone()
    except TypeError:
        chat_id = await init_new_chat(session, user_id)

    await add_message(session, text, "user", chat_id)
    messages = await get_chat_messages(session, chat_id)
    new_mess = send_messages(messages)
    await session.commit()
    return new_mess




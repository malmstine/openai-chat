import datetime
import sqlalchemy as sa

from openai_chat.db.models import chat_table, active_chat_table, message_table, users
from openai_chat.chat import send_messages
from openai_chat.exceptions import NotFound


async def init_new_chat(session, user_id, system_role=None):
    ex = await session.execute(
        chat_table.insert().values(system_role=system_role).returning(chat_table.c.id)
    )
    [chat_id] = ex.fetchone()

    ex = await session.execute(
        active_chat_table.select().where(active_chat_table.c.user_id == user_id)
    )

    if list(ex):
        await session.execute(
            active_chat_table.update()
            .values(active_chat=chat_id)
            .where(active_chat_table.c.user_id == user_id)
        )
    else:
        await session.execute(
            active_chat_table.insert().values(user_id=user_id, active_chat=chat_id)
        )

    await session.commit()
    return chat_id


async def add_message(session, content, role, chat_id):
    await session.execute(
        message_table.insert().values(
            content=content, role=role, created=datetime.datetime.now(), chat_id=chat_id
        )
    )
    await session.commit()


async def get_chat_messages(session, chat_id):
    system_role = await session.execute(
        chat_table.select()
        .with_only_columns(chat_table.c.system_role)
        .where(chat_table.c.id == chat_id)
    )
    system_role = system_role.scalar()
    ex = await session.execute(
        message_table.select()
        .with_only_columns(message_table.c.role, message_table.c.content)
        .where(message_table.c.chat_id == chat_id)
    )
    res = []
    for role, content in ex.fetchall():
        res.append(dict(role=role, content=content))
    return res, system_role


async def answer_bot(session, user_id, text, message_sender=send_messages):
    ex = await session.execute(
        active_chat_table.select()
        .with_only_columns(active_chat_table.c.active_chat)
        .where(active_chat_table.c.user_id == user_id)
    )
    try:
        [chat_id] = ex.fetchone()
    except TypeError:
        chat_id = await init_new_chat(session, user_id)

    await add_message(session, text, "user", chat_id)
    messages, system_role = await get_chat_messages(session, chat_id)
    if system_role:
        messages.insert(
            0,
            dict(
                role="system",
                content=system_role,
            ),
        )
    new_mess = message_sender(messages)
    await session.commit()
    return new_mess


async def set_user_active(session, t_user_id: int, active: bool = False) -> None:
    res = await session.execute(
        users.update().values(active=active).where(users.c.telegram_user_id == t_user_id)
    )
    if res.rowcount != 0:
        return

    if not active:
        raise NotFound

    await session.execute(
        users.insert().values(telegram_user_id=t_user_id, active=active)
    )


async def get_active_user_ids(session) -> list[int]:
    res = await session.execute(
        sa.select(users.c.telegram_user_id).where(users.c.active)
    )
    return res.scalars()


async def get_user_status(session) -> list[str]:
    res = await session.execute(
        users.select()
    )
    return [
        f"user_id={row.telegram_user_id}, active={row.active}" for row in res
    ]

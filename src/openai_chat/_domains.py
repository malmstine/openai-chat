import dataclasses
import datetime
import decimal
import logging
import typing as t

from openai_chat.chat import send_messages
from openai_chat.db import models
from openai_chat.exceptions import NotFound
import openai_chat.models as dmodels

logger = logging.getLogger(__name__)


async def create_new_chat(session, user_id, system_role) -> str:
    current_chat_model_stmt = await session.execute(
        models.user.select()
        .where(
            models.user.c.telegram_user_id == user_id
        )
        .with_only_columns(models.user.c.current_chat_model)
    )

    current_chat_model = current_chat_model_stmt.scalar()

    res = await session.execute(
        models.discussion.insert()
        .values(system_role=system_role, user=user_id, chat_model=current_chat_model)
        .returning(models.discussion.c.id)
    )
    discussion_id = res.scalar()

    await session.execute(models.user.update().values(current_discussion=discussion_id))

    return current_chat_model


async def get_active_user_ids(session) -> t.List[int]:
    res = await session.execute(
        models.user.select().where(models.user.c.is_active).with_only_columns(models.user.c.telegram_user_id)
    )
    return res.scalars()


async def get_current_discussion(session, user_id: int):
    res = await session.execute(
        models.discussion.select().where(
            models.discussion.c.id
            == models.user.select().where(models.user.c.telegram_user_id == user_id).with_only_columns(models.user.c.current_discussion)
        )
    )
    if not res.rowcount:
        raise NotFound

    return res.one()


async def get_discussion_messages(session, discussion_id):
    res = await session.execute(
        models.message.select().where(models.message.c.discussion == discussion_id)
    )
    return list(res)


async def save_messages(session, messages: t.List[dmodels.Message]) -> None:
    not_saved_values = [message for message in messages if message.id is None]

    await session.execute(models.message.insert().values(not_saved_values))


async def get_chat_models(session):
    return await session.execute(models.chat_model.select())


async def set_chat_model(session, user_id, chat_model):
    await session.execute(
        models.user.update()
        .values(current_chat_model=chat_model)
        .where(models.user.c.telegram_user_id == user_id)
    )


async def save_message(session, discussion_id, role, content, created: datetime.datetime = None):
    if created is None:
        created = datetime.datetime.now()

    res = await session.execute(
        models.message.insert().values(
            content=content,
            role=role,
            created=created,
            discussion=discussion_id
        ).returning(models.message.c.id)
    )
    return res.scalar()


async def answer(session, user_id: int, message: str):

    discussion_id, system_role, _, model_code = await get_current_discussion(session, user_id)

    await save_message(session, discussion_id, role="user", content=message)

    messages = await get_discussion_messages(session, discussion_id)

    message_ids = [message_id for message_id, *_ in messages]

    messages = [
        dict(role=role, content=content)
        for message_id, content, role, created, discussion in messages
    ]

    if system_role:
        messages.insert(
            0,
            dict(role="system", content=system_role)
        )

    ret = await send_messages(messages, model_code)

    answer_id = await save_message(
        session,
        discussion_id,
        role=ret.choices[0].message.role,
        content=ret.choices[0].message.content
    )

    cursor = await session.execute(
        models.chat_model.select().where(models.chat_model.c.code == model_code).with_only_columns(
            models.chat_model.c.in_cost, models.chat_model.c.out_cost
        )
    )
    in_cost, out_cost = cursor.one()

    await session.execute(
        models.transaction.insert().values(
            id=ret.id,
            created=datetime.datetime.fromtimestamp(ret.created),
            user=user_id,
            chat_model=model_code,
            in_message_ids=message_ids,
            out_message_id=answer_id,
            in_cost=in_cost,
            out_cost=out_cost,
            in_used_tokens=ret.usage.prompt_tokens,
            out_used_tokens=ret.usage.completion_tokens,
        )
    )
    return ret.choices[0].message.content


@dataclasses.dataclass
class Transaction:
    id: str
    created: datetime.datetime
    user_id: int
    chat_model: str
    in_message_ids: t.List[int]
    out_message_id: int
    in_used_tokens: int
    out_used_tokens: int
    in_cost: str
    out_cost: str

    @property
    def summary_usages(self) -> decimal.Decimal:
        count, *_ = self.in_cost.lstrip("$").split()
        in_used_cost = decimal.Decimal(count)

        count, *_ = self.out_cost.lstrip("$").split()
        out_used_cost = decimal.Decimal(count)

        return self.in_used_tokens * in_used_cost / 1000000 + self.out_used_tokens * out_used_cost / 1000000


async def get_usage(session, user_id: int):
    cursor = await session.execute(
        models.transaction.select().where(models.transaction.c.user == user_id)
    )
    transactions = [
        Transaction(*data)
        for data in cursor
    ]
    return sum(trans.summary_usages for trans in transactions)


async def usage_limits(session, user_id: int) -> decimal.Decimal:
    cursor = await session.execute(
        models.user.select().where(
            models.user.c.telegram_user_id == user_id
        ).with_only_columns(models.user.c.usage_limit)
    )
    return cursor.scalar()


import sqlalchemy


metadata = sqlalchemy.MetaData(schema="openai_chat")


chat_table = sqlalchemy.Table(
    "chat",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column("system_role", sqlalchemy.Text, default=sqlalchemy.Null),
)


message_table = sqlalchemy.Table(
    "message",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column("content", sqlalchemy.Text),
    sqlalchemy.Column("role", sqlalchemy.Text),
    sqlalchemy.Column("created", sqlalchemy.DateTime),
    sqlalchemy.Column("chat_id", sqlalchemy.ForeignKey("chat.id")),
)


active_chat_table = sqlalchemy.Table(
    "active_chat",
    metadata,
    sqlalchemy.Column("user_id", sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column("active_chat", sqlalchemy.ForeignKey("chat.id")),
)


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column(
        "telegram_user_id", sqlalchemy.BigInteger, primary_key=True, autoincrement=False
    ),
    sqlalchemy.Column("active", sqlalchemy.Boolean),
)

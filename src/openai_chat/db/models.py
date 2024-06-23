import sqlalchemy


metadata = sqlalchemy.MetaData(schema="openai_chat")


user = sqlalchemy.Table(
    "user",
    metadata,
    sqlalchemy.Column(
        "telegram_user_id", sqlalchemy.BigInteger, primary_key=True, autoincrement=False
    ),
    sqlalchemy.Column("name", sqlalchemy.VARCHAR),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean),
    sqlalchemy.Column(
        "current_discussion", sqlalchemy.ForeignKey("discussion.id", use_alter=True), nullable=True,
    ),
    sqlalchemy.Column(
        "current_chat_model", sqlalchemy.ForeignKey("chat_model.code"), nullable=False
    ),
    sqlalchemy.Column("usage_limit", sqlalchemy.DECIMAL),
)


discussion = sqlalchemy.Table(
    "discussion",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column("system_role", sqlalchemy.Text, nullable=True),
    sqlalchemy.Column("user", sqlalchemy.ForeignKey("user.telegram_user_id")),
    sqlalchemy.Column("chat_model", sqlalchemy.ForeignKey("chat_model.code")),
)


message = sqlalchemy.Table(
    "message",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column("content", sqlalchemy.Text),
    sqlalchemy.Column("role", sqlalchemy.Text),
    sqlalchemy.Column("created", sqlalchemy.DateTime),
    sqlalchemy.Column("discussion", sqlalchemy.ForeignKey("discussion.id")),
)


chat_model = sqlalchemy.Table(
    "chat_model",
    metadata,
    sqlalchemy.Column("code", sqlalchemy.Text, primary_key=True),
    sqlalchemy.Column("in_cost", sqlalchemy.VARCHAR),
    sqlalchemy.Column("out_cost", sqlalchemy.VARCHAR),
    sqlalchemy.Column("description", sqlalchemy.Text),
)


transaction = sqlalchemy.Table(
    "transaction",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.VARCHAR, primary_key=True),
    sqlalchemy.Column("created", sqlalchemy.DateTime),
    sqlalchemy.Column("user", sqlalchemy.ForeignKey("user.telegram_user_id")),
    sqlalchemy.Column("chat_model", sqlalchemy.ForeignKey("chat_model.code")),
    sqlalchemy.Column("in_message_ids", sqlalchemy.ARRAY(sqlalchemy.Integer)),
    sqlalchemy.Column("out_message_id", sqlalchemy.Integer),
    sqlalchemy.Column("in_used_tokens", sqlalchemy.Integer),
    sqlalchemy.Column("out_used_tokens", sqlalchemy.Integer),
    sqlalchemy.Column("in_cost", sqlalchemy.VARCHAR),
    sqlalchemy.Column("out_cost", sqlalchemy.VARCHAR),
)

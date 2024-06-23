from logging.config import fileConfig

import sqlalchemy
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from openai_chat.db.models import metadata
from dotenv import dotenv_values

from pathlib import Path

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

source_dir = Path(__file__).parent.parent.resolve() / ".env"
env_values = dotenv_values(source_dir)


section = config.config_ini_section
config.set_section_option(section, "DB_USER", env_values.get("DB_USER"))
config.set_section_option(section, "DB_PASS", env_values.get("DB_PASS"))
config.set_section_option(section, "DB_NAME", env_values.get("DB_NAME"))
config.set_section_option(section, "DB_PORT", str(env_values.get("DB_PORT")))
config.set_section_option(section, "DB_HOST", env_values.get("DB_HOST"))
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = [metadata]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

AUTOGENERATE_SCHEMAS = ["openai_chat"]


def include_name(name, type_, parent_names):
    """Функция, которая позволяет явно указать схему для генерации миграций"""
    if type_ == "schema":
        return name in AUTOGENERATE_SCHEMAS
    else:
        return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema="openai_chat",
        compare_type=True,
        include_schemas=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        connection.execute(sqlalchemy.text("CREATE SCHEMA IF NOT EXISTS openai_chat"))
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema="openai_chat",
            compare_type=True,
            include_schemas=True,
            include_name=include_name,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

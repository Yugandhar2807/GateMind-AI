import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402

import os

config = context.config

# Pull the DB URL from our own .env-driven settings instead of alembic.ini,
# so there is exactly one place credentials are configured.
# ALEMBIC_DB_URL_OVERRIDE is a dev-only escape hatch (e.g. to autogenerate/verify
# migrations against a throwaway SQLite file before a real MySQL password exists).
config.set_main_option(
    "sqlalchemy.url", os.environ.get("ALEMBIC_DB_URL_OVERRIDE") or settings.SQLALCHEMY_DATABASE_URI
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

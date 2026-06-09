from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.BaseMetadata
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

# Load .env file
load_dotenv(ROOT_DIR / ".env")

# Import Base from the same path models use: 'from database import Base' (not 'from src.database import Base')
# This ensures models share the same Base instance with the env.py metadata.
import database  # noqa: F811
Base = database.Base
# Import all models to register them with Base.metadata
import models  # noqa: F401
# Also import matcher module which has tables referenced by FK from production models
# but is NOT included in models/__init__.py
import models.matcher  # noqa: F401

target_metadata = Base.metadata
POSTGRES_ASYNC_PREFIX = "postgresql+asyncpg://"
POSTGRES_SYNC_PREFIX = "postgresql://"


def _to_sync_postgresql_url(url: str) -> str:
    if url.startswith(POSTGRES_ASYNC_PREFIX):
        return url.replace(POSTGRES_ASYNC_PREFIX, POSTGRES_SYNC_PREFIX, 1)
    return url


def _resolve_alembic_database_url() -> str:
    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError("CID Alembic migrations require PostgreSQL.")
    if url.startswith(POSTGRES_ASYNC_PREFIX) or url.startswith(POSTGRES_SYNC_PREFIX):
        return _to_sync_postgresql_url(url)
    raise RuntimeError("CID Alembic migrations require PostgreSQL.")


def _include_object(object, name, type_, reflected, compare_to):
    # Exclude everything in public schema.
    if hasattr(object, "schema") and object.schema == "public":
        return False

    # Exclude n8n_ tables.
    if type_ == "table" and name.startswith("n8n_"):
        return False

    # Exclude alembic_version table (internal Alembic table).
    if type_ == "table" and name == "alembic_version":
        return False

    return True


config.set_main_option("sqlalchemy.url", _resolve_alembic_database_url())


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=False,
        include_object=_include_object,
        version_table_schema="cid",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
        connect_args={"options": "-c search_path=cid"},
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=False,
            include_object=_include_object,
            version_table_schema="cid",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

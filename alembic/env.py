from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path
from dotenv import load_dotenv

from alembic import context
from sqlalchemy import pool, create_engine

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

# Load .env file
load_dotenv(ROOT_DIR / ".env")

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# For Alembic, we use a synchronous SQLite URL pointing to the absolute path of the database
database_url = os.getenv("DATABASE_URL")
if database_url:
    if database_url.startswith("sqlite+aiosqlite:///"):
        # Extract the relative path (everything after sqlite+aiosqlite:///)
        relative_path = database_url[len("sqlite+aiosqlite:///"):]
        # Make it absolute relative to the project root (ROOT_DIR)
        # If the relative_path is already absolute, we keep it, but note that it's relative to the current filesystem root.
        # However, the relative_path from the URL is likely relative to the current working directory.
        # We'll resolve it relative to ROOT_DIR to be safe.
        if not os.path.isabs(relative_path):
            absolute_path = (ROOT_DIR / relative_path).resolve()
        else:
            absolute_path = Path(relative_path).resolve()
        # Form the SQLAlchemy SQLite URL for an absolute path: sqlite:////<absolute_path>
        # Note: For absolute paths, we need four slashes: sqlite:////absolute/path/to/db
        database_url = f"sqlite:////{absolute_path}"
    # If it's already a synchronous SQLite URL, we might still need to make the path absolute.
    elif database_url.startswith("sqlite:///"):
        relative_path = database_url[len("sqlite:///"):]
        if not os.path.isabs(relative_path):
            absolute_path = (ROOT_DIR / relative_path).resolve()
            database_url = f"sqlite:////{absolute_path}"
        # If it's already absolute, we leave it as is (but note: the URL for absolute path should have four slashes? Actually, sqlite:///absolute/path is not correct; it should be sqlite:////absolute/path)
        # However, if the user provided an absolute path in the URL, it might already be in the correct format.
        # We'll assume that if it's sqlite:/// and the path is absolute, then it's missing a slash.
        # But to keep it simple, we'll only adjust if it's not absolute.
    # If it's not a SQLite URL, we leave it as is (for other databases, but we don't support them in this project).
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
        connect_args={"check_same_thread": False},
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=None,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

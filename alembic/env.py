from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool, create_engine
from dotenv import load_dotenv

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

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# For Alembic, we need a synchronous URL.
# Load the original DATABASE_URL from environment.
database_url = os.getenv("DATABASE_URL")
# Convert asyncpg URL to synchronous PostgreSQL URL if needed.
if database_url and database_url.startswith("postgresql+asyncpg://"):
    # Replace the driver to use psycopg2 (synchronous) for Alembic.
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
# For SQLite, we already handle absolute path conversion below.
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
config.set_main_option("sqlalchemy.url", database_url)


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
    
    def include_object(object, name, type_, reflected, compare_to):
        """
        Determine if an object should be included in the migration.
        
        Exclude:
        - All objects in the 'public' schema
        - All tables starting with 'n8n_'
        """
        # Exclude everything in public schema
        if hasattr(object, 'schema') and object.schema == 'public':
            return False
        
        # Exclude n8n_ tables
        if type_ == "table" and name.startswith("n8n_"):
            return False
        
        # Exclude alembic_version table (internal Alembic table)
        if type_ == "table" and name == "alembic_version":
            return False
            
        return True
    
    is_pg = url.startswith("postgresql")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=False,
        include_object=include_object,
        **(dict(version_table_schema="cid") if is_pg else {}),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Determine if we are using PostgreSQL to avoid SQLite-specific connect args
    url = config.get_main_option("sqlalchemy.url")
    
    def include_object(object, name, type_, reflected, compare_to):
        """
        Determine if an object should be included in the migration.
        
        Exclude:
        - All objects in the 'public' schema
        - All tables starting with 'n8n_'
        """
        # Exclude everything in public schema
        if hasattr(object, 'schema') and object.schema == 'public':
            return False
        
        # Exclude n8n_ tables
        if type_ == "table" and name.startswith("n8n_"):
            return False
        
        # Exclude alembic_version table (internal Alembic table)
        if type_ == "table" and name == "alembic_version":
            return False
            
        return True
    
    is_pg = url.startswith("postgresql")
    if is_pg:
        connect_args = {"options": "-c search_path=cid"}
    else:
        connect_args = {"check_same_thread": False}

    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=False,
            include_object=include_object,
            **(dict(version_table_schema="cid") if is_pg else {}),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
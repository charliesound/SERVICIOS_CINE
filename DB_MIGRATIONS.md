# Database Configuration & Migrations

## Quick Start

### SQLite (Default - Development)

```bash
# Default SQLite database
python -m uvicorn app:app --host 127.0.0.1 --port 8000

# With explicit SQLite
export DATABASE_URL="sqlite+aiosqlite:///./ailinkcinema.db"
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### PostgreSQL (Production)

```bash
# Set environment variable
export DATABASE_URL="postgresql+asyncpg://user:password@host:5432/dbname"

# Run migrations
python -m alembic upgrade head

# Start server
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

## Supported Database Drivers

| Driver | URL Format | Use Case |
|--------|------------|----------|
| SQLite | `sqlite+aiosqlite:///./filename.db` | Development |
| PostgreSQL | `postgresql+asyncpg://user:pass@host:5432/dbname` | Production |

## Migration Commands

### Apply all migrations
```bash
python -m alembic upgrade head
```

### Check current version
```bash
python -m alembic current
```

### Create new migration
```bash
python -m alembic revision --autogenerate -m "description"
```

### Rollback one version
```bash
python -m alembic downgrade -1
```

## Configuration

The database URL is read from:
1. Environment variable `DATABASE_URL`
2. Fallback: `config.yaml` settings

Validation is performed at startup:
- SQLite must use `sqlite+aiosqlite://`
- PostgreSQL must use `postgresql+asyncpg://`

## SQLite Bootstrap

When using SQLite, the application applies a non-destructive bootstrap that:
- Creates tables if they don't exist
- Adds missing columns to existing tables
- Creates indexes
- Does NOT drop or modify existing data

This allows schema evolution without manual migrations for development.

## PostgreSQL Migrations

For PostgreSQL, use Alembic migrations exclusively:
1. `alembic/env.py` reads `DATABASE_URL` from environment/config
2. All schema changes should be done via migrations
3. Run `alembic upgrade head` after deploying

## Files

- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Migration environment
- `alembic/versions/` - Migration scripts

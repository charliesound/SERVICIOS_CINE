# CID PostgreSQL-Only Alembic Alignment v1

Status: CANONICAL / MIGRATIONS
Date: 2026-06-09
Base commit: aee6bec

## Central Declaration

New CID migrations must be PostgreSQL-only. Alembic must not provide SQLite fallbacks, runtime branches, or compatibility paths for new SaaS phases.

## Context

- PostgreSQL-only canonical policy closed at `4d593fd`.
- Runtime/config PostgreSQL-only closed at `a325995`.
- Tests quarantine closed at `0e05b11`.
- Smoke scripts quarantine closed at `aee6bec`.

## Audit Findings

- `alembic/env.py` had active SQLite URL normalization and SQLite `connect_args` branches.
- `alembic.ini` had an unsafe concrete database URL and must use placeholder/env resolution.
- `alembic/versions/6ba14a0d02b6_add_matcher_jobs_table_and_matcher_job_.py` contains historical SQLite branches and must not be used as precedent for new migrations.

## Rules

- Alembic env must require a PostgreSQL URL.
- Canonical external URL is `postgresql+asyncpg://`.
- Alembic may convert `postgresql+asyncpg://` to a synchronous PostgreSQL driver URL internally only for Alembic engine creation.
- No SQLite fallback for missing `DATABASE_URL`.
- No path normalization for file databases.
- No new migration scripts may branch on SQLite dialect.
- Historical branches remain quarantined until a dedicated migration cleanup phase.

## Acceptance Gates

- `python -m py_compile alembic/env.py`
- `bash scripts/dev/guard_no_sqlite_regressions.sh`
- `git diff --check`
- No DB mutation and no Alembic upgrade in this phase

## Non-goals

- No DB upgrade
- No schema changes
- No migration rewrite
- No runtime/config changes
- No tests changes
- No Docker/.env changes

## Roadmap

1. `CID.SAAS.POSTGRESQL.ONLY.ALEMBIC.HISTORICAL.MIGRATION.QUARANTINE.1`
2. `CID.SAAS.POSTGRESQL.ONLY.ALEMBIC.POSTGRES.DRYRUN.1`
3. `CID.SAAS.POSTGRESQL.ONLY.INTEGRATION.TESTS.POSTGRES.MIGRATION.1`

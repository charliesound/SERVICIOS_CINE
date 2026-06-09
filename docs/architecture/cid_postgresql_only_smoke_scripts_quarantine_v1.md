# CID PostgreSQL-Only Smoke Scripts Quarantine v1

Status: CANONICAL / OPERATIONS
Date: 2026-06-09
Base commit: 0e05b11

## Central Declaration

New smoke/dev scripts for CID SaaS must not default to SQLite. They must require `postgresql+asyncpg://` `DATABASE_URL` or be explicitly classified as legacy quarantine.

## Context

- Runtime/config PostgreSQL-only closed in `a325995`.
- Tests SQLite legacy entered quarantine in `0e05b11`.
- Legacy smoke scripts still contain SQLite defaults and direct `sqlite3` access.

## Classification

### A. PostgreSQL-valid / neutral scripts

- `scripts/healthcheck_stack.sh`
- `scripts/smoke_data_stack.sh`
- `scripts/smoke_n8n_stack.sh`
- `scripts/start_stack.sh`
- `scripts/dev/guard_wsl_repo.sh`
- `scripts/dev/guard_no_sqlite_regressions.sh`, as a guard-only exception

### B. Historical migration exception

- `scripts/db/migrate_sqlite_to_postgres_cid.py`

This is the only migration bridge allowed to reference SQLite intentionally.

### C. Legacy smoke quarantine

- `scripts/inspect_editorial_state.py`
- `scripts/smoke_fcpxml_real_paths.py`
- `scripts/smoke_davinci_multiplatform_package.py`
- `scripts/smoke_dual_system_reconcile.py`
- `scripts/smoke_storyboard_modes.py`
- `scripts/smoke_editorial_package.py`
- `scripts/smoke_sprint13_rc.py`
- `scripts/certify_release_demo.sh`
- `scripts/materialize_legacy_storyboard_shots.py`
- `scripts/smoke_production_real_fixture.py`
- `scripts/smoke_dual_system_fcpxml.py`
- `scripts/seed_presentation_visual_smoke.py`
- `scripts/smoke_restart_recovery.py`
- `scripts/smoke_editorial_mvp.py`
- `scripts/smoke_review_delivery_persistence.py`
- `scripts/smoke_producer_persistence.py`

### D. Diagnostic script to align

- `scripts/diagnose_database_config.py`

It must no longer resolve SQLite paths or import `IS_SQLITE`.

## Acceptance Rules

- Quarantined scripts must not be used as proof for PostgreSQL-only SaaS acceptance gates.
- New scripts must not use `sqlite`, `sqlite3`, `aiosqlite`, `.db` defaults, or `sqlite+aiosqlite`.
- Database-backed smoke scripts must either:
  1. require `DATABASE_URL` or `TEST_DATABASE_URL` with `postgresql+asyncpg://`, or
  2. explicitly skip or fail with a clear PostgreSQL-only message.
- No fallback to SQLite is allowed.

## Non-goals

- No migration of legacy smoke scripts in this phase
- No deletion of scripts
- No runtime/config changes
- No Alembic changes
- No tests changes
- No Docker changes

## Roadmap

1. `CID.SAAS.POSTGRESQL.ONLY.SMOKE.SCRIPTS.EDITORIAL.POSTGRES.1`
2. `CID.SAAS.POSTGRESQL.ONLY.SMOKE.SCRIPTS.STORYBOARD.POSTGRES.1`
3. `CID.SAAS.POSTGRESQL.ONLY.SMOKE.SCRIPTS.PRODUCTION.POSTGRES.1`
4. `CID.SAAS.POSTGRESQL.ONLY.ALEMBIC.ALIGNMENT.1`
5. `CID.SAAS.POSTGRESQL.ONLY.INTEGRATION.TESTS.POSTGRES.MIGRATION.1`

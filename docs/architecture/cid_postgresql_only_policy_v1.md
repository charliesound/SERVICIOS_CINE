# CID PostgreSQL-Only Policy v1

Version: 1.0
Status: CANONICAL / ARCHITECTURE
Date: 2026-06-09
Owners: CID Architecture / CID Product / CID Business
Scope: canonical policy for PostgreSQL as the only active database backend for all new CID SaaS work
Supersedes: docs/architecture/cid_database_canonical_policy_v1.md (historical transition context only)

## 1. Central Declaration

PostgreSQL is the only active database backend for CID runtime, SaaS development, new tests, locking semantics, ledger/accounting, AI jobs, migrations, and production-like validation.

This policy is mandatory for all new phases starting from CID.SAAS.POSTGRESQL.ONLY.CANONICALIZATION.1.

## 2. Prohibitions

The following patterns are forbidden in any new phase code, tests, scripts, or runtime configuration:

- SQLite runtime usage
- SQLite fallback or degradation
- SQLite test backend for new phases
- sqlite+aiosqlite connection strings
- sqlite:// connection strings
- aiosqlite in new backend/test work
- _is_sqlite helper methods
- IS_SQLITE flags
- SQLITE_LEGACY_BOOTSTRAP flags
- Any degradation to SQLite logic

Existing historical references are handled under legacy quarantine (section 5).

## 3. Permitted Exceptions

SQLite may appear only in the following contexts:

- Historical docs: docs/validation/ or old phase reports that document past state
- Explicit migration scripts: one-way scripts from SQLite to PostgreSQL (e.g., scripts/db/migrate_sqlite_to_postgres_cid.py)
- Archived legacy tests/scripts: explicitly marked as legacy quarantine with a comment like LEGACY QUARANTINE - DO NOT USE IN NEW PHASES
- Policy mentions: references to SQLite only when stating it is forbidden or documenting historical context

## 4. AI Jobs Rule

AIJobRepository and all future gateway/orchestration/ledger integration must use PostgreSQL locking semantics, especially SELECT ... FOR UPDATE / stmt.with_for_update().

No SQLite fallback, no _is_sqlite() detection, no dialect-aware branching for locking.

## 5. Test Rule

New integration tests must use the PostgreSQL test harness.

- If TEST_DATABASE_URL is missing, PostgreSQL-specific tests may skip.
- Tests must never fallback to SQLite.
- Unit tests using fakes/spies are unrestricted (they do not touch a real database).

## 6. Legacy Quarantine Inventory

The following categories contain historical SQLite remnants. They are quarantined for future cleanup, not for immediate removal.

### 6.1 Runtime/config legacy remnants

- src/database.py: IS_SQLITE flag, SQLite bootstrap paths (CID.SAAS.POSTGRESQL.ONLY.RUNTIME.CONFIG.1)
- src/config.py: SQLite-aware config (CID.SAAS.POSTGRESQL.ONLY.RUNTIME.CONFIG.1)
- src/core/config.py: SQLite-aware config (CID.SAAS.POSTGRESQL.ONLY.RUNTIME.CONFIG.1)
- src/config/config.yaml: SQLite defaults (CID.SAAS.POSTGRESQL.ONLY.RUNTIME.CONFIG.1)

### 6.2 Integration tests

- Tests that force sqlite in DATABASE_URL need quarantine or PostgreSQL harness.
- Phase: CID.SAAS.POSTGRESQL.ONLY.TESTS.QUARANTINE.1

### 6.3 Smoke scripts

- Scripts that create .db files need alignment.
- Phase: CID.SAAS.POSTGRESQL.ONLY.SMOKE.SCRIPTS.ALIGNMENT.1

### 6.4 Alembic

- alembic/env.py may contain SQLite compatibility branches.
- Phase: CID.SAAS.POSTGRESQL.ONLY.ALEMBIC.ALIGNMENT.1

### 6.5 Historical docs

- docs/validation/ and old release docs may reference SQLite.
- Phase: CID.SAAS.POSTGRESQL.ONLY.DOCS.LEGACY.QUARANTINE.1

## 7. Future Cleanup Roadmap

1. CID.SAAS.POSTGRESQL.ONLY.RUNTIME.CONFIG.1: Clean src/database.py, src/config.py, src/core/config.py, src/config/config.yaml
2. CID.SAAS.POSTGRESQL.ONLY.TESTS.QUARANTINE.1: Quarantine or migrate integration tests using SQLite
3. CID.SAAS.POSTGRESQL.ONLY.ALEMBIC.ALIGNMENT.1: Remove SQLite branches from alembic/env.py
4. CID.SAAS.POSTGRESQL.ONLY.SMOKE.SCRIPTS.ALIGNMENT.1: Align smoke scripts to PostgreSQL
5. CID.SAAS.POSTGRESQL.ONLY.DOCS.LEGACY.QUARANTINE.1: Mark historical docs as legacy

## 8. Guardrail

A lightweight bash guard (scripts/dev/guard_no_sqlite_regressions.sh) scans staged or working-tree diffs for new SQLite introductions outside the allowlist. This guard must pass before any commit in new phases.

## 9. References

- docs/architecture/cid_database_canonical_policy_v1.md (superseded, historical context)
- docs/architecture/cid_ai_job_repository_async_contract_v1.md (locking contract)
- scripts/dev/guard_no_sqlite_regressions.sh (regression guard)

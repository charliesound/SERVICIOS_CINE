# CID Database Canonical Policy v1

> **SUPERSEDED**: This document is superseded for future work by
> docs/architecture/cid_postgresql_only_policy_v1.md.
> Any older allowance for SQLite legacy/local/test fallback is obsolete
> for new CID SaaS phases.
> Keep this document only as historical transition context.

## Objective
Establish PostgreSQL as the canonical database for CID production environments
and define the transition path from the current SQLite/PostgreSQL dual reality.

## Current state (verified by CID.BASELINE.SAFETY.CANONICALIZATION.1)

- `.env` points to PostgreSQL (`postgresql+asyncpg://`)
- `compose.base.yml` defaults to SQLite (`sqlite+aiosqlite:///./ailinkcinema_s2.db`)
- PostgreSQL service is **commented out** in `compose.base.yml`
- Multiple `.db` files exist (8+ files in repo root + subdirectories)
- Active SQLite DB: `ailinkcinema_s2.db` (37MB)

## Canonical policy

### 1. PostgreSQL is production canonical
- All new development targets PostgreSQL
- All Alembic migrations run against PostgreSQL
- All production/staging deployments use PostgreSQL
- CID schemas use `cid.*` namespace where applicable

### 2. SQLite is legacy/local/backup ONLY
- SQLite is permitted for:
  - Local development (fast iteration)
  - Test suites (isolated per test)
  - Backup/restore workflows
  - Read-only diagnostics
- SQLite MUST NOT be used for production deployments

### 3. Do NOT modify in this phase
- Do NOT delete any `.db` files
- Do NOT uncomment PostgreSQL in compose files
- Do NOT run Alembic migrations to switch databases
- Do NOT change `DATABASE_URL` defaults in compose files

### 4. n8n separation
- n8n has its own schema in PostgreSQL (`n8n.*`) or its own database
- n8n MUST NOT share CID application schemas
- n8n can write to CID DB via API only, never direct schema access

### 5. Migration criteria (future phase)
Before removing SQLite from compose:
- [ ] All 24+ Alembic migrations applied and verified on PostgreSQL
- [ ] Data from `ailinkcinema_s2.db` migrated to PostgreSQL
- [ ] Smoke/validation scripts pass against PostgreSQL
- [ ] Docker Compose health checks pass with PostgreSQL only
- [ ] Rollback plan documented and tested

### 6. .db files freeze list

| File | Status | Action |
|---|---|---|
| `ailinkcinema_s2.db` | ACTIVE | Freeze until migration |
| `ailinkcinema.db` | ORPHAN | Delete after migration |
| `ailinkcinema_fixed.db` | ORPHAN | Delete after migration |
| `ailinkcinema_s2_new.db` | ORPHAN | Delete after migration |
| `test_alembic.db` | TEST | Evaluate after migration |
| `ailinkcinema_s2.backup-*.db` | BACKUP | Archive post-migration |
| `ailinkcinema_s2.runtime-backup-*.db` | BACKUP | Archive post-migration |
| `src/ailinkcinema.db` | ORPHAN | Delete after migration |
| `cid-budget/*/test_budget.db` | SATELLITE | Per satellite project policy |

## References
- `CID.BASELINE.SAFETY.CANONICALIZATION.1` sections 5-6
- `compose.base.yml` lines 21 (SQLite default), line 26 (volume mount)
- `.env` line `DATABASE_URL`

# Enterprise Audit Report — CID Budget Estimator

**Auditor:** OpenCode Senior Backend Auditor  
**Date:** 2026-05-12  
**Scope:** `cid-budget/` backend + CID App Registry (`src/services/app_registry.py`)  
**Version:** 1.0.0  

---

## 1. Executive Summary

The backend compiles cleanly, passes 13/13 integration tests, and has a solid foundation (JWT auth, async httpx, PostgreSQL, Alembic, rate limiting, structured logging). However, it has **5 critical (P0)** and **8 high (P1)** findings that block production deployment.

**Overall readiness:** 30%  
**GO for production:** NO  
**Estimated remediation:** 40-60 hours across 10 engineering phases

---

## 2. Audit Command Trace

All commands below were executed in `/opt/SERVICIOS_CINE` unless noted.

```bash
# 1. Python compilation check
python -m compileall cid-budget/backend/ -q          # OK

# 2. Test suite
cd cid-budget && python -m pytest tests/ -v --tb=short  # 13/13 passed

# 3. Alembic migration check
cd cid-budget/backend && python -m alembic current    # FAILED — psycopg2 not installed

# 4. File structure
find cid-budget -type f -not -path '*__pycache__*' -not -path '*.pyc' | sort

# 5. Git status
git status --short

# 6. Docker compose validation
docker compose config                                # OK (version attr obsolete)

# 7. Route enumeration
python -c "import sys; sys.path.insert(0,'cid-budget/backend'); from app.main import app; [print(r.methods, r.path) for r in app.routes if hasattr(r,'methods')]"

# 8. Security grep
grep -rn 'os\.getenv\|except.*:\s*pass\|allow_origins\|create_engine\|require_auth' cid-budget/backend/ --include='*.py'
```

---

## 3. Evidence Matrix

### Dimension 1: FastAPI App Startup (`main.py`)

| Check | Status | Evidence |
|-------|--------|----------|
| App factory pattern | ❌ | `app = FastAPI()` at module level, no `create_app()` |
| Lifespan context manager | ✅ | `@asynccontextmanager async def lifespan()` at line 31 |
| Graceful shutdown | ⚠️ | `engine.dispose()` called, but no timeout, no SIGTERM handler |
| Startup sequence | ⚠️ | DB init + config validation, but no connectivity retry for Postgres |
| Module-level globals | ❌ | `SessionLocal = None`, `engine = None` at module scope (lines 18-19) |

### Dimension 2: Configuration (`core.py`, env vars)

| Check | Status | Evidence |
|-------|--------|----------|
| Pydantic Settings | ❌ | Raw `os.getenv()` in 11 locations across 4 files |
| Environment separation | ❌ | No dev/staging/prod distinction |
| Secret validation | ❌ | `JWT_SECRET` defaults to `""` — silent auth bypass in prod |
| Typed config | ❌ | `RATE_LIMIT_PER_MINUTE = int(os.getenv(...))` can crash on bad input |
| CORS production default | ❌ | `CORS_ORIGINS` defaults to `"*"` in docker-compose.yml:26 |
| `.env` support | ❌ | No `.env` file loaded by FastAPI (no `python-dotenv` in requirements) |

### Dimension 3: Auth / JWT (`core.py:27-38`)

| Check | Status | Evidence |
|-------|--------|----------|
| JWT signature verification | ✅ | `pyjwt.decode(token, secret, algorithms=[...])` |
| Expiration check | ✅ | `except ExpiredSignatureError` handled |
| Issuer validation | ❌ | No `issuer` parameter, no `options={"verify_iss": True}` |
| Audience validation | ❌ | No `audience` parameter |
| Not-Before (nbf) | ❌ | No `nbf` verification enabled |
| Key rotation support | ❌ | Single static secret, no JWKS endpoint |
| Roles / scopes | ❌ | Token returns raw payload, no RBAC mapping |
| Token blacklist | ❌ | No revocation mechanism |
| Auth header in logs | ❌ | `authorization[:20]` logged at main.py:77 |

### Dimension 4: PostgreSQL (`main.py:22-28`, `models.py`)

| Check | Status | Evidence |
|-------|--------|----------|
| Async engine | ❌ | `create_engine` (sync) at line 25, not `create_async_engine` |
| Connection pooling | ⚠️ | `pool_size=5, max_overflow=10`, but no `pool_recycle` |
| Pool pre-ping | ✅ | `pool_pre_ping=True` |
| Connection timeout | ❌ | No `connect_timeout` or `pool_timeout` |
| Index coverage | ⚠️ | Only `project_id` and `budget_estimate_id` indexed (2 indexes) |
| Foreign key constraints | ❌ | `budget_line_items.budget_estimate_id` has no FK to `budget_estimates.id` |
| Unique constraints | ❌ | No unique constraint preventing multiple active budgets per project |
| Soft delete | ❌ | No `deleted_at` or `is_deleted` column |
| `created_at`/`updated_at` | ⚠️ | Python-side defaults, not server-side `now()` |

### Dimension 5: Alembic (`alembic/`)

| Check | Status | Evidence |
|-------|--------|----------|
| Configuration file | ✅ | `alembic.ini` present |
| env.py | ✅ | Reads `DATABASE_URL` from env, respects override |
| Initial migration | ✅ | `001_initial_schema.py` with both tables |
| Migrations runnable | ❌ | Fails with `ModuleNotFoundError: psycopg2` — env.py connects automatically |
| Upgrade/downgrade test | ❌ | No test in test suite |
| Multiple migration files | ❌ | Only 1 migration, no lineage |

### Dimension 6: Tests (`tests/test_api.py`)

| Check | Status | Evidence |
|-------|--------|----------|
| Total tests | 13 | All passing |
| Auth tests | 3 | unauthorized_without_token, unauthorized_bad_token, list_templates (authenticated) |
| CRUD tests | 6 | generate, list, get, activate, recalculate, archive |
| Validation tests | 2 | invalid_level, budget_not_found |
| Multi-project test | 1 | multiple_budgets_per_project |
| Multi-tenant isolation | ❌ | Not tested |
| Migration test | ❌ | Not tested |
| Rate limit test | ❌ | Not tested |
| Soft delete test | ❌ | Not tested |
| Load test | ❌ | Not tested |
| DB dialect | ⚠️ | Uses SQLite, not PostgreSQL |

### Dimension 7: Docker (`backend/Dockerfile`)

| Check | Status | Evidence |
|-------|--------|----------|
| Multi-stage build | ❌ | Single-stage `FROM python:3.12-slim` |
| Non-root user | ❌ | No `USER` directive — runs as root |
| Healthcheck | ❌ | No `HEALTHCHECK` instruction in Dockerfile |
| Graceful shutdown | ❌ | No `STOPSIGNAL` or timeout |
| Dependency caching | ❌ | `pip install` before `COPY . .` ✅ (layer caching OK) |
| `--no-cache-dir` | ✅ | Used in pip install |
| Exposed port | ✅ | `EXPOSE 8500` |
| Read-only filesystem | ❌ | No `--read-only` flag |

### Dimension 8: docker-compose (`docker-compose.yml`)

| Check | Status | Evidence |
|-------|--------|----------|
| PostgreSQL healthcheck | ✅ | `pg_isready` with 5s interval |
| API healthcheck | ✅ | curl to `/health` |
| depends_on condition | ✅ | `condition: service_healthy` |
| JWT_SECRET empty default | ❌ | `JWT_SECRET=${JWT_SECRET:-}` — empty in dev, no warning |
| CORS default `*` | ❌ | `CORS_ORIGINS=${CORS_ORIGINS:-*}` |
| Network isolation | ❌ | Default network, no explicit internal network |
| Volume mounts | ✅ | Named volume `pgdata` for Postgres |
| `version` attribute | ❌ | `version: "3.9"` is obsolete (docker warning) |
| Resource limits | ❌ | No `mem_limit` or `cpus` for any service |

### Dimension 9: Frontend + nginx (`frontend/Dockerfile`)

| Check | Status | Evidence |
|-------|--------|----------|
| Build-time env | ✅ | `VITE_API_URL` as build arg |
| Production nginx | ✅ | Multistage to nginx:alpine |
| gzip compression | ✅ | Enabled for JS/CSS/JSON/SVG |
| CSP header | ❌ | Missing |
| HSTS header | ❌ | Missing |
| X-XSS-Protection | ❌ | Missing |
| X-Frame-Options | ✅ | `SAMEORIGIN` |
| X-Content-Type-Options | ✅ | `nosniff` |
| Referrer-Policy | ❌ | Missing |

### Dimension 10: Logging & Observability

| Check | Status | Evidence |
|-------|--------|----------|
| Structured (JSON) logging | ❌ | Plain text `%(asctime)s [%(levelname)s]` format |
| Request ID correlation | ❌ | No `request_id` middleware |
| Log level configurable | ✅ | `LOG_LEVEL` env var |
| Prometheus metrics | ❌ | No `/metrics` endpoint |
| OpenTelemetry | ❌ | No instrumentation |
| Auth token masking | ❌ | First 20 chars of `Authorization` header logged raw |

### Dimension 11: Health Checks

| Check | Status | Evidence |
|-------|--------|----------|
| Single `/health` | ✅ | Exists at `main.py:81` |
| Liveness endpoint | ❌ | No `/health/live` (is process alive?) |
| Readiness endpoint | ❌ | No `/health/ready` (can serve traffic?) |
| Startup endpoint | ❌ | No `/health/startup` (initialized fully?) |
| DB dependency | ✅ | Verifies `SELECT 1` |
| Dependencies check | ⚠️ | Only checks DB, no Redis/MinIO (not yet added) |

### Dimension 12: Async Correctness

| Check | Status | Evidence |
|-------|--------|----------|
| Sync DB in async routes | ❌ | All `db.execute()` calls are sync, blocking event loop |
| httpx client | ✅ | `httpx.AsyncClient` used in App Registry |
| asyncio.gather | ✅ | Used for concurrent health checks |
| Sync `create_engine` | ❌ | Not `create_async_engine` from `sqlalchemy.ext.asyncio` |

### Dimension 13: Route Protection

| Check | Status | Evidence |
|-------|--------|----------|
| Routes requiring auth | 8/9 | All except `/health` have `Depends(require_auth)` |
| Duplicate route | ❌ | `/templates` registered twice (lines 119 and 186) |
| Rate limiting applied | ✅ | Middleware covers all routes |
| CORS applied | ✅ | Middleware configured |
| API versioning | ❌ | No `/api/v1/` prefix |

### Dimension 14: Multi-tenancy

| Check | Status | Evidence |
|-------|--------|----------|
| `organization_id` column | ⚠️ | Present but `nullable=True` |
| Tenant isolation | ❌ | No filter enforces `organization_id = current_org` |
| `project_id` scoped to org | ❌ | Anyone can query any `project_id` |
| Tenant context middleware | ❌ | Not implemented |

### Dimension 15: OpenAPI

| Check | Status | Evidence |
|-------|--------|----------|
| Auto-generated docs | ✅ | `/docs`, `/redoc`, `/openapi.json` |
| Route count | 14 | One is duplicate `/templates` |
| Tags | ✅ | `budget` tag applied |
| Response models | ❌ | Not specified (raw dicts returned) |
| Version prefix | ❌ | `/api/budget/...` no `/api/v1/budget/...` |

---

## 4. Risk Classification

### P0 — Critical (blocking production)

| ID | Risk | File:Line | Impact |
|----|------|-----------|--------|
| **R01** | Config raw os.getenv, no Pydantic Settings — silent failures | `core.py:6-11` | Missing secret in prod = auth bypass → data breach |
| **R02** | Duplicate `/templates` route registered twice | `routes.py:119+186` | Dead code, confusing behavior, wasted route table |
| **R03** | Sync SQLAlchemy engine in async FastAPI | `main.py:25` | Blocks event loop under load → request timeout → cascading failure |
| **R04** | No multi-tenancy — `organization_id` nullable | `models.py:16` | Any user can access any project's budget → data leakage |
| **R05** | JWT no issuer/audience validation | `core.py:33` | Stolen token from any service can access budget API |

### P1 — High (week 1-2)

| ID | Risk | File:Line | Impact |
|----|------|-----------|--------|
| **R06** | Rate limit in-memory dict, not Redis | `main.py:54` | Reset on restart, not shared across workers |
| **R07** | No request_id in logs | `main.py:72-77` | Cannot trace request across services |
| **R08** | Error responses inconsistent, no global handler | `routes.py` | API consumers get mixed formats |
| **R09** | CORS default `*` in production | `docker-compose.yml:26` | XSS / data exfiltration vector |
| **R10** | Docker runs as root, single-stage | `Dockerfile` | Security audit failure, 1GB+ image |
| **R11** | Alembic cannot run (psycopg2 not installed) | `alembic/env.py:29` | Cannot apply migrations in CI/CD |
| **R12** | Auth token partially logged | `main.py:77` | Credential leakage in log files |
| **R13** | No health/live, /health/ready separation | `main.py:81` | Kubernetes probes cannot work |

### P2 — Medium (week 3-4)

| ID | Risk | File:Line | Impact |
|----|------|-----------|--------|
| **R14** | No structured JSON logging | `core.py:15-18` | Cannot ship logs to Loki/ELK |
| **R15** | No Prometheus metrics | — | No monitoring/alerts |
| **R16** | No DB pool_recycle/connect_timeout | `main.py:25` | Stale connections behind PgBouncer |
| **R17** | Missing DB foreign key constraint | `models.py` | Orphaned line items possible |
| **R18** | No migration upgrade/downgrade test | `tests/` | Schema drift undetected |
| **R19** | No soft delete | `models.py` | Accidental data loss irreversible |
| **R20** | No API version prefix | `routes.py` | Breaking changes impossible |
| **R21** | No security headers (CSP, HSTS, XSS) | `frontend/Dockerfile` | XSS vulnerability in SPA |
| **R22** | No CI/CD pipeline | — | Manual deploy risk |
| **R23** | No backup/restore scripts | — | No disaster recovery |

---

## 5. Route Audit

```
GET  /health                          → unprotected  ✅
GET  /api/budget/templates            → auth required ✅  (DUPLICATE x2 ❌)
GET  /api/budget/projects/{id}        → auth required ✅
GET  /api/budget/projects/{id}/active → auth required ✅
POST /api/budget/projects/{id}/generate → auth required ✅
GET  /api/budget/{id}                 → auth required ✅
POST /api/budget/{id}/activate        → auth required ✅
POST /api/budget/{id}/recalculate     → auth required ✅
POST /api/budget/{id}/archive         → auth required ✅
```

All business routes are protected. Only `/health` is public.  
**One critical finding:** `/templates` registered twice — second registration is dead code.

---

## 6. OpenAPI Snapshot

Collected via `python -c "from app.main import app; [print(r.methods, r.path) for r in app.routes if hasattr(r,'methods')]"`:

| # | Method(s) | Path |
|---|-----------|------|
| 1 | GET, HEAD | `/openapi.json` |
| 2 | GET, HEAD | `/docs` |
| 3 | GET, HEAD | `/docs/oauth2-redirect` |
| 4 | GET, HEAD | `/redoc` |
| 5 | GET | `/health` |
| 6 | GET | `/api/budget/projects/{project_id}` |
| 7 | GET | `/api/budget/projects/{project_id}/active` |
| 8 | POST | `/api/budget/projects/{project_id}/generate` |
| 9 | GET | `/api/budget/templates` |
| 10 | GET | `/api/budget/{budget_id}` |
| 11 | POST | `/api/budget/{budget_id}/activate` |
| 12 | POST | `/api/budget/{budget_id}/recalculate` |
| 13 | POST | `/api/budget/{budget_id}/archive` |
| 14 | GET | `/api/budget/templates` ← **DUPLICATE** |

---

## 7. File-by-File Risk

| File | Lines | Risk | Key issues |
|------|-------|------|------------|
| `main.py` | 97 | **P0** | Sync engine, no app factory, bare except, token in logs |
| `core.py` | 38 | **P0** | Raw os.getenv, JWT no issuer/audience |
| `models.py` | 50 | **P0** | organization_id nullable, no FK, no soft delete |
| `routes.py` | 196 | **P0** | Duplicate /templates, sync DB calls in async routes |
| `services.py` | 206 | **P2** | No async, no tenant filter |
| `Dockerfile` | 7 | **P1** | Root user, single-stage, no healthcheck |
| `docker-compose.yml` | 48 | **P1** | CORS `*`, JWT empty default, obsolete version attr |
| `alembic/env.py` | 39 | **P1** | Fails without psycopg2 installed |
| `frontend/Dockerfile` | 25 | **P2** | Missing CSP, HSTS, XSS headers |
| `tests/test_api.py` | 148 | **P2** | No multi-tenant, migration, or load tests |

---

## 8. Required Fixes by Phase

```
Phase 1: Config + App Factory   → R01, R09, R13      (8h)
Phase 2: Security Enterprise    → R05, R08, R12, R21  (12h)
Phase 3: Multi-tenancy          → R04                 (8h)
Phase 4: Database Enterprise    → R03, R16, R17, R19  (10h)
Phase 5: Job Queue              → (new)               (8h)
Phase 6: Storage                → (new)               (6h)
Phase 7: Observability          → R07, R14, R15       (8h)
Phase 8: API Contract           → R02, R20            (4h)
Phase 9: Deployment             → R06, R10, R11, R22  (8h)
Phase 10: Hardening             → R23                 (4h)
```

**Total estimate: 76 hours**

---

## 9. GO / NO-GO

### NO-GO for production ❌

The following P0 risks must be resolved before any production traffic:

| P0 | Risk | Minimum fix |
|----|------|-------------|
| R01 | Config raw os.getenv | Pydantic Settings with strict validation |
| R02 | Duplicate /templates | Remove dead route |
| R03 | Sync SQLAlchemy | `create_async_engine` + async session |
| R04 | organization_id nullable | Required field + tenant filter middleware |
| R05 | JWT weak validation | Full iss/aud/exp/nbf validation |

**Minimum effort to GO: 20 hours (Phases 1-2)**

### GO for Phase 1 (Config + App Factory) ✅

- [x] Tests pass (13/13)
- [x] compileall passes
- [x] No business logic changes needed
- [x] Refactoring isolated to `app/core/` and `app/middleware/`

**Recommendation:** Approve Phase 1 immediately.

---

## 10. Reproducible Audit Commands

```bash
# Verify compilation
python -m compileall cid-budget/backend/ -q

# Run tests
cd cid-budget && python -m pytest tests/ -v --tb=short

# Check routes (including duplicates)
cd cid-budget/backend && python -c "
import sys; sys.path.insert(0,'.');
from app.main import app;
for r in app.routes:
    if hasattr(r, 'methods'):
        ms = ','.join(sorted(r.methods - {'HEAD'}) or ['?'])
        print(f'  {ms:8s} {r.path}')
print(f'Total: {len([r for r in app.routes if hasattr(r,\"methods\")])}')
"

# Check duplicate routes
grep -n '@router\.\(get\|post\)' app/routes.py | sort | uniq -d

# Check unprotected routes
grep -B1 'async def [a-z]' app/routes.py | grep -v 'require_auth\|def \|--'

# Security header grep
grep -rn 'os\.getenv\|except.*:\s*pass\|allow_origins\s*=\s*\"\*\"' app/ --include='*.py'

# Docker security
grep 'USER\|HEALTHCHECK\|STOPSIGNAL\|--read-only' Dockerfile

# Alembic check
python -m alembic current 2>&1
```

---

## Appendix A: Files Inspected (27 total)

```
cid-budget/backend/app/main.py
cid-budget/backend/app/core.py
cid-budget/backend/app/models.py
cid-budget/backend/app/routes.py
cid-budget/backend/app/services.py
cid-budget/backend/requirements.txt
cid-budget/backend/Dockerfile
cid-budget/backend/alembic.ini
cid-budget/backend/alembic/env.py
cid-budget/backend/alembic/script.py.mako
cid-budget/backend/alembic/versions/001_initial_schema.py
cid-budget/docker-compose.yml
cid-budget/cid-manifest.json
cid-budget/README.md
cid-budget/frontend/Dockerfile
cid-budget/frontend/package.json
cid-budget/frontend/vite.config.ts
cid-budget/frontend/src/api.ts
cid-budget/frontend/src/App.tsx
cid-budget/frontend/src/pages/BudgetEstimator.tsx
cid-budget/frontend/index.html
cid-budget/frontend/tailwind.config.js
cid-budget/tests/test_api.py
src/services/app_registry.py
src/routes/app_registry_routes.py
src/app.py
```

## Appendix B: Dependencies

**Backend (6):** fastapi, uvicorn, sqlalchemy, psycopg2-binary, pyjwt, alembic  
**Missing:** pydantic-settings, python-dotenv, asyncpg, redis, prometheus-client, opentelemetry-*

**Frontend (3):** react, react-dom, lucide-react  
**Missing:** @tanstack/react-query, axios (uses raw fetch), react-router

---

*Audit completed by OpenCode Senior Backend Auditor. All commands reproducible.*

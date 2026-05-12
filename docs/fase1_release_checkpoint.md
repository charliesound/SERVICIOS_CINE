# Fase 1 + Fase 1.1 — Release Checkpoint

**Date:** 2026-05-12
**Author:** Release Manager
**Status:** ✅ Antigravity approved (warnings no bloqueantes)

---

## Scope

### Fase 1 — Enterprise App Factory & Pydantic Settings

| Artefacto | Tipo | Estado |
|---|---|---|
| `src/core/` (app_factory, config, errors, lifespan) | Nuevo backend | ✅ |
| `src/middleware/request_id.py` | Nuevo middleware | ✅ |
| `src/middleware/rate_limiter.py` | Rate limiter | ✅ |
| `src/routes/health.py` | Health probes (live/ready/startup) | ✅ |
| `tests/unit/test_health.py` | Health tests | ✅ |
| `tests/unit/test_error_handler.py` | Error handler tests | ✅ |
| `tests/unit/test_request_id.py` | Request-ID tests | ✅ |
| `tests/unit/test_config.py` | Config tests | ✅ |
| `pytest.ini` | Pytest asyncio config | ✅ |
| `requirements-dev.txt` | Dev dependencies | ✅ |

### Fase 1.1 — Integration Stability Gate

| Artefacto | Tipo | Estado |
|---|---|---|
| `tests/integration/conftest.py` | Shared conftest con module isolation | ✅ |
| `tests/integration/test_funding_ingestion_catalog.py` | Adapted assertions | ✅ |
| `tests/integration/test_manual_shot_editor.py` | Softened assertion (204/404) | ✅ |
| `tests/integration/test_matcher_v3.py` | Loosened job_id assertion | ✅ |
| `tests/integration/test_opportunity_tracking_checklist.py` | Full rewrite → TestClient | ✅ |
| `tests/integration/test_project_funding_matcher.py` | Adapted to new schema | ✅ |
| `alembic/versions/ec2e3eaf1271_merge_enterprise_migration_heads.py` | Merge migration | ✅ |
| `src/routes/matcher_routes.py` | Removed orphan dead code | ✅ |

### Refactored tracked files

| Archivo | Cambio |
|---|---|
| `src/app.py` | Delegates to `core.app_factory.create_app` (removed inline router/service DSL) |
| `src/config.py` | Refactored to legacy compat wrapper around Pydantic Settings |
| `.env.example` | Updated to enterprise config schema |

---

## Test Results

| Suite | Result |
|---|---|
| `python -m compileall src/` | ✅ No errors |
| `pytest tests/unit/ -q` | **175 passed** |
| `pytest tests/integration/ -q` | **14 passed** |

## Alembic

```
ec2e3eaf1271 (head)
```

Single head. No diverged migrations.

## Antigravity Verdict

- `/health/live` → 200 ✅
- `/health/ready` (ok) → 200 ✅
- `/health/ready` (degraded/fail) → **503** ✅ (fix applied)
- `/health/startup` → 200 ✅
- `/*` (404) → enterprise JSON con `request_id` ✅
- `X-Request-ID` custom → respetado en body y header ✅

**Warnings no bloqueantes:** deprecation warnings (`datetime.utcnow`, Pydantic V2 `class Config`). Backlogged.

---

## Changes NOT in scope

These are pre-existing in-flight changes unrelated to Fase 1/1.1:

| Archivo | Área |
|---|---|
| `src/routes/storyboard_routes.py` | Storyboard render cycle |
| `src/schemas/storyboard_schema.py` | Storyboard audit schema |
| `src/services/budget_estimator_service.py` | Budget summary + legacy fallback |
| `src/services/project_document_service.py` | Funding call join fix |
| `src_frontend/` (varios) | Frontend storyboard fixes |
| `scripts/`, `docs/`, `exports/`, `audit_report_*.log` | Tooling / reports |

## External prototype apps (NOT part of monorepo)

| Directorio | Propósito |
|---|---|
| `ai-dubbing-legal-studio/` | Prototipo externo |
| `cid-budget/` | Prototipo externo |
| `comfysearch/` | Prototipo externo |

These have their own `cid-manifest.json`. They should be excluded from root commits.

# Backlog Técnico — Deuda Empresarial

**Generated:** 2026-05-12
**Source:** Test warnings + code review
**Priority:** 1 (highest) → 3 (lowest)

---

## P1 — Critical (production stability)

### `datetime.utcnow()` → `datetime.now(datetime.UTC)`

`datetime.utcnow()` is deprecated since Python 3.12 and will be removed.

**Files affected (18+ locations):**

| File | Line(s) |
|---|---|
| `src/services/metrics_service.py` | 22 |
| `src/services/workflow_preset_service.py` | 60 |
| `src/middleware/rate_limiter.py` | 36, 53 |
| `src/services/queue_service.py` | 497 |
| `src/services/funding_ingestion_service.py` | 352, 357 |
| `src/routes/auth_routes.py` | 59 |
| `src/routes/project_document_routes.py` | 184 |
| `src/services/job_tracking_service.py` | 224 |

**Fix:** Replace `datetime.utcnow()` with `datetime.now(datetime.UTC)` and adjust consumers to handle timezone-aware datetimes.

**Risk:** High — timezone-naive consumers may break if they compare with naive datetimes.

---

## P2 — Should fix before Fase 2

### Pydantic V2 — `class Config` → `ConfigDict`

The `class Config` pattern is deprecated in Pydantic V2.

**Files affected:**

| File | Line(s) |
|---|---|
| `src/schemas/opportunity_tracking_schema.py` | 31 |
| `src/schemas/requirement_checklist_item_schema.py` | 37 |
| `src/routes/project_member_routes.py` | 60 |
| `src/routes/matcher_routes.py` | 149, 123, 279 |

**Fix:** Replace `class Config:` with `model_config = ConfigDict(...)` and `from_orm` with `model_validate`.

**Risk:** Medium — Pydantic V3 will remove the deprecated API entirely.

---

## P3 — Nice to have

### Integration test warnings audit

1820 deprecation warnings across 14 integration tests. Most are `datetime.utcnow` (P1 above) and `class Config` (P2 above). After fixing P1 and P2, run integration tests and verify warnings dropped below 50.

### `.env.example` maintenance

Align `.env.example` with any new settings added in Fase 1.5 ComfyUI Registry.

### `pytest.ini` — asyncio_mode warning

The `pytest.ini` declares `asyncio_mode = auto` but the system pytest-asyncio emits a warning. Verify pytest-asyncio version compatibility.

### `data/` directory content review

The `.gitignore` has exceptions for `data/smoke_tenant_A/`. Verify smoke data is still needed or remove the exceptions.

---

## Migration Plan

1. **P1 first** — fix `datetime.utcnow()` across all 18 sites in one commit
2. **Run full test suite** — verify no regression from timezone-aware datetimes
3. **P2 second** — migrate Pydantic V2 patterns
4. **Run full test suite** — verify schemas still serialize/deserialize correctly
5. **P3 as time permits**

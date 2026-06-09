# CID PostgreSQL-Only Tests Quarantine v1

Status: CANONICAL / TESTING
Date: 2026-06-09
Base commit: a325995

## Central Declaration

New CID SaaS backend tests must use PostgreSQL semantics or the PostgreSQL test harness. Legacy SQLite tests are not valid acceptance gates for new SaaS phases.

## Context

- Runtime/config PostgreSQL-only was closed in `a325995`.
- `_bootstrap_sqlite_schema` was removed from runtime.
- Any test that still depends on that path is legacy quarantine.

## Classification

### A. PostgreSQL-valid tests

- `tests/helpers/postgres_test_harness.py`
- `tests/unit/test_postgres_test_harness.py`
- `tests/unit/test_config.py` after `a325995`
- `tests/integration/test_credit_ledger_postgres.py`
- `tests/unit/test_ai_job_repository.py`, with the note that its SQLite mention is only a negative source assertion, not a backend dependency.

### B. Legacy SQLite quarantine - integration

- `tests/integration/conftest.py`
- `tests/integration/test_manual_shot_editor.py`
- `tests/integration/test_script_analysis_export.py`
- `tests/integration/test_project_document_rag.py`
- `tests/integration/test_google_drive_connectors.py`
- `tests/integration/test_funding_dossier_export.py`
- `tests/integration/test_script_analysis_enforcement.py`
- `tests/integration/test_project_script_analysis_flow.py`
- `tests/integration/test_funding_ingestion_catalog.py`
- `tests/integration/test_matcher_v3.py`
- `tests/integration/test_project_private_documents.py`
- `tests/integration/test_project_funding_matcher.py`
- `tests/integration/test_breakdown_export.py`
- `tests/integration/test_presentation_visual_validation.py`

### C. Legacy SQLite quarantine - unit

- `tests/unit/test_project_visual_bible_service.py`
- `tests/unit/test_auth_password_reset.py`
- `tests/unit/test_queue_service_sqlite_retry.py`
- `tests/unit/test_character_bible_openapi_routes.py`

### D. Allowed negative PostgreSQL-only assertions

- `tests/helpers/postgres_test_harness.py`
- `tests/unit/test_postgres_test_harness.py`
- `tests/unit/test_ai_job_repository.py`

These may mention SQLite only to reject it or assert absence of SQLite helpers.

## Acceptance Rule

New SaaS phases must not use quarantined tests as proof of correctness.

New persistence, concurrency, accounting, and tenant-safety tests must use PostgreSQL or the PostgreSQL test harness.

If `TEST_DATABASE_URL` is missing, PostgreSQL-required tests may skip, but must never fallback to SQLite.

## Explicit Non-goals

- No migration of integration tests in this phase
- No deletion of legacy tests
- No runtime/config changes
- No Alembic changes
- No smoke script changes

## Roadmap

1. `CID.SAAS.POSTGRESQL.ONLY.INTEGRATION.TESTS.POSTGRES.MIGRATION.1`
2. `CID.SAAS.POSTGRESQL.ONLY.LEGACY.SQLITE.TESTS.ARCHIVE.1`
3. `CID.SAAS.POSTGRESQL.ONLY.SMOKE.SCRIPTS.ALIGNMENT.1`
4. `CID.SAAS.POSTGRESQL.ONLY.ALEMBIC.ALIGNMENT.1`

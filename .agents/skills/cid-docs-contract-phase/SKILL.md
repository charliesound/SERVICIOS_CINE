---
name: cid-docs-contract-phase
description: Use this skill for documentation-only or contract/test-only phases in AILinkCinema/CID, especially before implementing runtime SaaS changes.
---

# CID Docs Contract Phase

Use this skill when creating architecture docs, product specs, legal specs, launch docs, runbooks, QA documents, or contract tests.

## Main principle

Documentation phases must not modify runtime behavior.

## Allowed by default

- `docs/**`
- `tests/unit/test_*_spec.py`
- `tests/unit/test_*_contract.py`
- `tests/unit/test_*_runbook.py`
- `tests/unit/test_*_qa.py`

## Forbidden by default

- Backend runtime code.
- Frontend runtime code.
- Database models.
- Alembic migrations.
- Docker.
- `.env`.
- Credentials.
- Production config.
- External network calls.
- Real CRM, Supabase, payment or n8n runtime changes.

## Document requirements

Each document should include:

1. Objective.
2. Current state.
3. Scope.
4. Non-goals.
5. User value.
6. Operational flow.
7. Risks.
8. Acceptance criteria.
9. Future phases.

## Test requirements

Create lightweight tests that verify:

- The document exists.
- Critical sections are present.
- Dangerous claims are absent.
- Forbidden runtime terms are not introduced when inappropriate.
- Spanish public-facing text uses correct accents and professional wording when applicable.

## Final response requirements

Explain clearly that the phase is documentary/test-only and that no runtime behavior was changed.

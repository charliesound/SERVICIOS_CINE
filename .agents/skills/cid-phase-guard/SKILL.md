---
name: cid-phase-guard
description: Use this skill before starting any AILinkCinema/CID development phase to define scope, no-goals, safety boundaries, validation commands, and commit/tag discipline.
---

# CID Phase Guard

Use this skill whenever the user asks to start, continue, implement, validate, audit, or close a development phase in the AILinkCinema/CID repository.

## Repository rules

- Work only inside `/opt/SERVICIOS_CINE`.
- Assume WSL Ubuntu.
- Activate `.venv` before Python commands.
- Do not use PowerShell.
- Do not use Windows drive paths, mounted Windows filesystem paths, or Windows network-style paths.
- Do not create `/opt/SERVICIOS_CINE/opt`.

## Default forbidden areas unless the phase explicitly allows them

Do not modify:

- `.env`
- Docker files
- Alembic migrations
- frontend runtime
- backend runtime
- production configuration
- database schema
- generated backups
- legacy local database files
- secrets
- credentials

## Required phase structure

Before editing files, produce:

1. Phase ID.
2. Goal.
3. Files expected to change.
4. Explicit no-goals.
5. Validation commands.
6. Expected final state.
7. Commit/tag proposal, but do not commit or tag unless the user explicitly approves.

## Safety rule

Prefer small, reversible changes. If the task can be done as documentation/test-only first, do that before runtime changes.

## Final response requirements

Always report:

- What changed.
- What was intentionally not changed.
- Validation results.
- Whether the workspace is clean or not.
- Suggested next phase.

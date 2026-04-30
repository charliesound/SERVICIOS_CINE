# Production Candidate Status - AILinkCinema

This document is the current operational reference for the gap between demo-ready and production-ready.

## Executive Status

- Controlled commercial demo readiness: YES
- Public production readiness: NO
- Full production-ready: NO

## Current Risk Map

### Closed for production candidate

- Demo routes are now disabled by default in production and must be enabled explicitly with `ENABLE_DEMO_ROUTES=1`.
- Experimental routes are disabled by default in production.
- Postproduction routes are disabled by default because the module remains a stub.
- Auth and app secrets can now be overridden from environment variables.

### Still open before claiming full production-ready

- Queue persistence now supports `db` mode with minimal restart recovery; `memory` remains demo/dev only.
- Billing remains internal/manual only; no real payment lifecycle exists.
- Postproduction remains non-production-ready by design.
- Demo seed flows must stay off in public production deployments.
- Rate limiting remains basic and in-memory.
- `APP_SECRET_KEY` must be defined explicitly to avoid inheriting `AUTH_SECRET_KEY`.
- `INTEGRATION_TOKEN_ENCRYPTION_KEY` and `GOOGLE_DRIVE_OAUTH_STATE_SECRET` remain pending if integrations are used.
- ComfyUI was not validated in the last smoke and remains optional for controlled demo.
- TLS/443 remains pending for public VPS exposure.
- Legal review remains pending.
- Legacy/artifact cleanup to `OLD` remains pending.

## Blocking Gaps

1. Backup/restore is basic and operator-driven, not automated.
2. Billing is commercial-demo only, not real subscription billing.
3. Postproduction is intentionally disabled pending real implementation.

## Operational Flags

### Demo / Internal environments

```bash
APP_ENV=demo
ENABLE_DEMO_ROUTES=1
ENABLE_EXPERIMENTAL_ROUTES=0
ENABLE_POSTPRODUCTION_ROUTES=0
QUEUE_PERSISTENCE_MODE=memory
```

### Production candidate deployments

```bash
APP_ENV=production
ENABLE_DEMO_ROUTES=0
ENABLE_EXPERIMENTAL_ROUTES=0
ENABLE_POSTPRODUCTION_ROUTES=0
QUEUE_PERSISTENCE_MODE=db
AUTH_SECRET_KEY=change-me
APP_SECRET_KEY=change-me-different
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Reference Smokes

- Demo certification: `scripts/smoke_sprint13_rc.py`
- Restart and recovery baseline: `scripts/smoke_restart_recovery.py` (`db` recovery + `memory` compatibility)

## Honest Demo Status

- Apt for controlled commercial demo
- Not public production
- Queue in `memory` mode remains an accepted demo constraint
- Rate limiter remains basic and in-memory
- ComfyUI is optional and was not validated in the last smoke
- TLS/443 remains pending
- Legal review remains pending
- OLD cleanup remains pending

## Historical Note

Some roadmap and strategy documents in the repository were written before later sprint implementation. When they conflict with current code, use this file plus `docs/SPRINT13_RUNBOOK.md` and `docs/RELEASE_DEMO_GUIDE.md` as the operational source of truth.

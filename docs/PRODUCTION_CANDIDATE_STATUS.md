# Production Candidate Status - AILinkCinema

This document is the current operational reference for the gap between demo-ready and production-ready.

## Executive Status

- Demo readiness: YES
- Production candidate: YES, with reduced risk after Sprint 13.2 hardening
- Full production-ready: NO

## Current Risk Map

### Closed for production candidate

- Demo routes are now disabled by default in production and must be enabled explicitly with `ENABLE_DEMO_ROUTES=1`.
- Experimental routes are disabled by default in production.
- Postproduction routes are disabled by default because the module remains a stub.
- Auth and app secrets can now be overridden from environment variables.

### Still open before claiming full production-ready

- Queue persistence remains `memory` mode; jobs are not durable across full process restarts.
- Billing remains internal/manual only; no real payment lifecycle exists.
- Postproduction remains non-production-ready by design.
- Demo seed flows must stay off in public production deployments.

## Blocking Gaps

1. Durable queue backend is not implemented yet.
2. Backup/restore is basic and operator-driven, not automated.
3. Billing is commercial-demo only, not real subscription billing.
4. Postproduction is intentionally disabled pending real implementation.

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
QUEUE_PERSISTENCE_MODE=memory
AUTH_SECRET_KEY=change-me
```

## Reference Smokes

- Demo certification: `scripts/smoke_sprint13_rc.py`
- Restart and recovery baseline: `scripts/smoke_restart_recovery.py`

## Historical Note

Some roadmap and strategy documents in the repository were written before later sprint implementation. When they conflict with current code, use this file plus `docs/SPRINT13_RUNBOOK.md` and `docs/RELEASE_DEMO_GUIDE.md` as the operational source of truth.

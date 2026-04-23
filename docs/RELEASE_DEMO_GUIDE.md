# Release Demo Guide - AILinkCinema

This guide covers everything needed to run an official AILinkCinema commercial demo.

## Quick Start

Run the certification script to validate the release:

```bash
cd /opt/SERVICIOS_CINE
bash scripts/certify_release_demo.sh
```

This validates:
- Backend smoke test (isolated SQLite in /tmp)
- Frontend build
- Documentation exists

## Demo Credentials

| Plan | Email | Password |
|------|-------|----------|
| Free | demo_free@servicios-cine.com | demo123 |
| Studio | demo_studio@servicios-cine.com | demo123 |
| Creator | demo_creator@servicios-cine.com | demo123 |
| Enterprise | demo_enterprise@servicios-cine.com | demo123 |
| Admin | admin@servicios-cine.com | admin123 |

## Demo Organization Label

All demo users are assigned to organizations prefixed with `OFFICIAL DEMO`, e.g., `OFFICIAL DEMO Org demo_studio`.

The company field displays `OFFICIAL DEMO` instead of generic "AILinkCinema Demo".

## Manually Starting the Platform

### Backend

```bash
cd /opt/SERVICIOS_CINE/src
./.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd /opt/SERVICIOS_CINE/src_frontend
npm run dev
```

### Seed Demo Data

```bash
curl -X POST http://127.0.0.1:8000/api/demo/quick-start
```

## Demo Walkthrough

### 1. Login
Navigate to the frontend and log in with `demo_studio@servicios-cine.com / demo123`.

### 2. Explore Dashboard
- View seeded projects: "Cine: Robot en Atardecer", "Storyboard: Escena de Acción", etc.
- Check presets: "Cinematic Portrait", "Fast Storyboard", "Voice Clone Basic"
- View recent demo jobs with various statuses

### 3. Create New Project
1. Click "New Project"
2. Enter name and description
3. Add script text
4. Run "Analyze" - extracts characters, locations, scenes
5. Run "Storyboard" - generates visual frames

### 4. Plan Upgrade Demo
1. Go to Plans page
2. Request upgrade to different plan
3. Verify plan change persists in database

### 5. Export Demo
1. Open any project
2. Export to JSON - structured project data
3. Export to ZIP - complete project bundle

## Smoke Test Details

The certification script runs `scripts/smoke_sprint13_rc.py` which:

1. Spins up isolated backend with fresh SQLite in `/tmp`
2. Seeds demo data via `/api/demo/quick-start`
3. Tests login flow
4. Validates plan change (free → producer → persists)
5. Creates project, analyzes, storyboards
6. Verifies jobs, assets, metrics generated
7. Exports JSON and ZIP formats

### Optional Smoke Test Variables

```bash
# Custom port
SMOKE_PORT=8015 src/.venv/bin/python scripts/smoke_sprint13_rc.py

# Keep database file after test
SMOKE_KEEP_DB=1 src/.venv/bin/python scripts/smoke_sprint13_rc.py

# Custom database
SMOKE_DATABASE_URL=sqlite+aiosqlite:////tmp/my_test.db src/.venv/bin/python scripts/smoke_sprint13_rc.py
```

## Frontend Build

To build frontend independently:

```bash
cd /opt/SERVICIOS_CINE
bash scripts/build_frontend_wsl.sh
```

Or directly:

```bash
cd /opt/SERVICIOS_CINE/src_frontend
npm run build
```

Output is in `src_frontend/dist/`.

## Troubleshooting

**Backend won't start**: Check Python venv is active at `src/.venv/bin/python`.

**Smoke test fails**: Verify no other service on port 8013, or set `SMOKE_PORT=8015`.

**Frontend build fails**: Run `npm install` in `src_frontend` first.

## Release Checklist

- [x] Demo seed uses OFFICIAL DEMO label
- [x] Demo users have proper organization names
- [x] Smoke test passes
- [x] Frontend builds successfully
- [x] This guide exists in docs/RELEASE_DEMO_GUIDE.md
- [x] Runbook exists at docs/SPRINT13_RUNBOOK.md

---

Last updated: Sprint 13 Closure
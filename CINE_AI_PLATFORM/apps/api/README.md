# CINE AI PLATFORM API

## Official backend boundary
- Official entrypoint: `src.app:app`
- Legacy alias entrypoint: `src.main:app` (compat only)

## Local run (WSL/Linux)

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn src.app:app --reload --host 127.0.0.1 --port 3000
```

## Local run (PowerShell)

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn src.app:app --reload --host 127.0.0.1 --port 3000
```

## Environment variables
- `APP_NAME`
- `APP_ENV`
- `API_HOST`
- `API_PORT`
- `CORS_ORIGINS` (comma separated)
- `FRONTEND_ORIGINS` (legacy alias, optional)
- `SHOTS_STORE_BACKEND`
- `SHOTS_JSON_FILE`
- `SHOTS_SQLITE_FILE`
- `RENDER_JOBS_SQLITE_FILE`
- `ENABLE_LEGACY_ROUTES` (`true` or `false`)
- `COMFYUI_BASE_URL` (ComfyUI HTTP endpoint, external to Docker)
- `COMFYUI_TIMEOUT_SECONDS`

## Official route groups
- Health/config: `/api/health`, `/api/health/details`, `/api/config`
- Storage-first API: `/api/storage/*`
- Shots API: `/api/shots*`
- Render jobs API: `/api/render/jobs*`

## Legacy isolated routes
- `/projects`, `/scenes`, `/shots`, `/jobs`
- Registered only when `ENABLE_LEGACY_ROUTES=true`

## Backend smoke check

```bash
cd apps/api
ENABLE_LEGACY_ROUTES=false python scripts/smoke_check.py
```

## Docker image
Build context is `apps/api` and runtime command is uvicorn on port `3000`.

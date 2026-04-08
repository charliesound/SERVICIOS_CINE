# CINE AI PLATFORM - setup real (Sprint 2)

This setup keeps ComfyUI outside Docker and uses backend as the only API boundary.

## Official runtime paths
- Frontend official: `apps/web/src/main.tsx` -> `apps/web/src/App.tsx`
- Backend official: `apps/api/src/app.py`

## 1) Local dev (without Docker)

### Backend (WSL/Linux)

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn src.app:app --reload --host 127.0.0.1 --port 3000
```

### Frontend (WSL/Linux)

```bash
cd apps/web
npm install
cp .env.example .env
npm run dev
```

## 2) Server mode (Windows + WSL + Docker Compose)

From repo root:

```bash
cp .env.compose.example .env.compose
docker compose --env-file .env.compose up -d --build
```

Endpoints:
- Frontend: `http://localhost:8080`
- Backend health: `http://localhost:3000/api/health`

If host port `3000` is already busy, set `API_PORT_BIND=3001` in `.env.compose`.

## 3) Validation checklist

### Frontend

```bash
cd apps/web
npm run lint
npm run build
```

### Backend smoke

```bash
cd apps/api
ENABLE_LEGACY_ROUTES=false python scripts/smoke_check.py
```

## 4) ComfyUI integration boundary
- ComfyUI is not deployed in Docker Compose.
- Backend reads `COMFYUI_BASE_URL` and is the only integration point.
- Recommended Compose value: `COMFYUI_BASE_URL=http://host.docker.internal:8188`.
- Do not expose ComfyUI directly to public internet.

## 5) Additional docs
- Backend contract and route boundary: `docs/api/backend_routes_contract.md`
- Operations runbook: `docs/ops/runbook_wsl.md`
- Render jobs contract: `docs/render/jobs_render_contract.md`
- Render lifecycle: `docs/render/jobs_render_lifecycle.md`

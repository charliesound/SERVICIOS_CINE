# Backend routes contract (Sprint 2)

## Objective
Define the official API boundary and isolate legacy routes without breaking current behavior.

## Official routes (supported)

### Platform and health
- `GET /api/health`
- `GET /api/health/details`
- `GET /api/ops/status`
- `GET /api/config`

### Storage-first API (official data contract)
- `GET /api/storage/info`
- `GET /api/storage/summary`
- `GET|PATCH /api/storage/project`
- `GET /api/storage/project/{project_id}/sequences`
- `GET /api/storage/project/{project_id}/scenes`
- `GET /api/storage/project/{project_id}/shots`
- `GET /api/storage/characters`
- `GET|POST|PATCH|DELETE /api/storage/character/{character_id}` (and collection endpoints)
- `GET /api/storage/sequences`
- `GET /api/storage/sequence/{sequence_id}`
- `GET /api/storage/sequence/{sequence_id}/scenes`
- `GET /api/storage/sequence/{sequence_id}/shots`
- `GET /api/storage/scenes`
- `GET /api/storage/scene/{scene_id}`
- `GET /api/storage/scene/{scene_id}/shots`
- `GET /api/storage/shots`
- `GET /api/storage/shot/{shot_id}`
- `POST|PATCH|DELETE /api/storage/sequence/{sequence_id}` (and collection endpoints)
- `POST|PATCH|DELETE /api/storage/scene/{scene_id}` (and collection endpoints)
- `POST|PATCH|DELETE /api/storage/shot/{shot_id}` (and collection endpoints)
- `POST /api/storage/migrate-json-to-sqlite`
- `POST /api/storage/seed-demo`
- `POST /api/storage/reset`
- `GET /api/storage/export-json`
- `POST /api/storage/import-json`

### Official shots API (non-legacy)
- `GET|POST /api/shots`
- `GET|PUT|PATCH|DELETE /api/shots/{shot_id}`

### Official render jobs API (MVP)
- `POST /api/render/jobs`
- `GET /api/render/jobs`
- `GET /api/render/jobs/{job_id}`
- `POST /api/render/jobs/{job_id}/retry`

## Compatibility routes (supported, but not preferred)
- `GET|POST|PATCH|DELETE /characters`
- `GET|PATCH|DELETE /characters/{character_id}`

## Legacy isolated routes
- `GET /projects`
- `GET /scenes`
- `GET|PUT /shots`
- `GET|PUT /shots/{shot_id}`
- `GET /jobs`

These routes are registered only when `ENABLE_LEGACY_ROUTES=true`.

## Runtime switches
- `ENABLE_LEGACY_ROUTES=true` -> keeps old mock endpoints available.
- `ENABLE_LEGACY_ROUTES=false` -> disables legacy routers at startup.

## ComfyUI boundary
- Backend is prepared for HTTP integration through `COMFYUI_BASE_URL`.
- ComfyUI is intentionally out of Docker and should not be exposed directly to the internet.
- Frontend must call backend endpoints only.

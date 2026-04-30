# Deploy VPS - AILinkCinema

This guide covers the approved VPS overlay for the current AILinkCinema / CID demo.

## Official Demo Stack

- VPS demo runtime: `compose.base.yml` + `compose.vps.yml`
- Official demo proxy: `Caddyfile.deploy`
- Official frontend: `src_frontend`
- Official backend: `src`

## Not Part of the Official Runtime

The following are outside the official runtime for this demo:

- `OLD/legacy_stacks/docker-compose.yml`
- `OLD/legacy_stacks/Caddyfile`
- `Web Ailink_Cinema`
- `CINE_AI_PLATFORM`
- `CID_SERVER/automation-engine`
- `automation-engine`
- `n8n`
- `qdrant`

## Prerequisites

1. VPS with Docker and Docker Compose available.
2. `.env` prepared from `.env.vps.example`.
3. Strong secrets generated before startup.
4. Domain and network exposure treated as controlled demo only.
5. ComfyUI only if the demo needs external real render.

## Required Variables

- `AUTH_SECRET_KEY`
- `APP_SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Rules:

- `AUTH_SECRET_KEY` must be strong, random and secret.
- `APP_SECRET_KEY` must be defined explicitly and must be different from `AUTH_SECRET_KEY`.
- The placeholders in `.env.vps.example` are not operational.
- Do not publish or version the real `.env` file.

### Integration Variables Only If Used

- `INTEGRATION_TOKEN_ENCRYPTION_KEY`
- `GOOGLE_DRIVE_OAUTH_STATE_SECRET`
- `GOOGLE_DRIVE_CLIENT_ID`
- `GOOGLE_DRIVE_CLIENT_SECRET`
- `COMFYUI_*` if the demo needs external real render

## Safe Startup Flow

```bash
cd /opt/SERVICIOS_CINE

# 1. Prepare environment
cp .env.vps.example .env

# 2. Replace placeholders with strong real secrets
#    AUTH_SECRET_KEY
#    APP_SECRET_KEY
#    ACCESS_TOKEN_EXPIRE_MINUTES
#    Configure COMFYUI_* only if external render is needed

# 3. Validate compose configuration
docker compose -f compose.base.yml -f compose.vps.yml config

# 4. Start the approved VPS demo runtime
docker compose -f compose.base.yml -f compose.vps.yml up -d --build

# 5. Check status
docker compose -f compose.base.yml -f compose.vps.yml ps
```

## Expected Demo Routes

- `/` -> official React/Vite frontend
- `/cid` -> official React/Vite frontend; real protection happens in the SPA
- `/register/select` -> official React/Vite frontend
- `/legal/privacidad` -> official React/Vite frontend
- `/api/health` -> backend OK
- `/health` -> backend OK
- `/docs` -> `404`
- `/openapi.json` -> `404`
- `/auth/login` -> `404`
- `/n8n` -> `404`
- `/qdrant` -> `404`
- `/automation` -> `404`

## Minimum Smoke Checklist

- `/` OK
- `/cid` OK
- `/register/select` OK
- `/legal/privacidad` OK
- `/api/health` OK
- `/health` OK
- `/docs` returns `404`
- `/openapi.json` returns `404`
- `/auth/login` returns `404`
- auth login OK
- pending blocked
- render without token returns `401`
- queue without token returns `401`

## TLS and Exposure Status

TLS/443 is still pending validation for this demo release. Treat the VPS runtime as controlled demo only, not public production. Do not claim public internet readiness from this overlay in its current state.

## ComfyUI Connectivity

Only validate ComfyUI connectivity if the demo requires external real render. If ComfyUI is not needed, the current demo can still be operated as a controlled commercial demo.

## What Must Never Be Published

- Real `.env`
- Secrets
- OAuth tokens
- SQLite databases with real data
- Uploaded documents
- User PDFs
- Logs with sensitive data
- Private client outputs

## Honest Demo Status

- Apt for controlled commercial demo
- Not public production
- ComfyUI is optional and was not validated in the last smoke
- Queue remains in `memory` mode
- Rate limiter remains basic and in-memory
- TLS/443 remains pending
- Legal review remains pending
- OLD cleanup remains pending

## See Also

- `docs/RELEASE_DEMO_GUIDE.md`
- `docs/PRODUCTION_CANDIDATE_STATUS.md`
- `docs/DEPLOY_HOME.md`

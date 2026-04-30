# Deploy Home Demo - AILinkCinema

This guide covers the approved home deployment for the current AILinkCinema / CID demo.

## Official Demo Stack

- Home demo runtime: `compose.base.yml` + `compose.home.yml`
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

`compose.home.tailscale.yml` can still be used later for optional remote ingress, but it is not part of the official runtime baseline approved for this demo.

## Prerequisites

1. Docker and Docker Compose available on the home machine.
2. `.env` prepared from `.env.home.example`.
3. Strong secrets generated before startup.
4. ComfyUI only if the demo needs external real render.

## Required Variables

- `AUTH_SECRET_KEY`
- `APP_SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Rules:

- `AUTH_SECRET_KEY` must be strong, random and secret.
- `APP_SECRET_KEY` must be defined explicitly and must be different from `AUTH_SECRET_KEY`.
- The placeholders in `.env.home.example` are not operational.
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
cp .env.home.example .env

# 2. Replace placeholders with strong real secrets
#    AUTH_SECRET_KEY
#    APP_SECRET_KEY
#    ACCESS_TOKEN_EXPIRE_MINUTES

# 3. Validate compose configuration
docker compose -f compose.base.yml -f compose.home.yml config

# 4. Start the approved home demo runtime
docker compose -f compose.base.yml -f compose.home.yml up -d --build

# 5. Check status
docker compose -f compose.base.yml -f compose.home.yml ps
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

```bash
curl -i http://localhost/
curl -i http://localhost/cid
curl -i http://localhost/register/select
curl -i http://localhost/legal/privacidad
curl -i http://localhost/api/health
curl -i http://localhost/health
curl -i http://localhost/docs
curl -i http://localhost/openapi.json
curl -i http://localhost/auth/login
```

Expected results:

- `/`, `/cid`, `/register/select`, `/legal/privacidad`, `/api/health`, `/health` -> OK
- `/docs`, `/openapi.json`, `/auth/login`, `/n8n`, `/qdrant`, `/automation` -> `404`
- auth login OK
- pending blocked
- render without token -> `401`
- queue without token -> `401`

## Optional Remote Access

Tailscale can be layered on later for controlled operator access. If used, treat it as an access option around the approved runtime, not as a separate official runtime.

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
- `docs/DEPLOY_VPS.md`

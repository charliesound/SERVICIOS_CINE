# Release Demo Guide - AILinkCinema

This guide is the minimum operational reference to run the approved AILinkCinema / CID demo.

## Official Demo Runtime

- Home demo: `compose.base.yml` + `compose.home.yml`
- VPS demo: `compose.base.yml` + `compose.vps.yml`
- Official demo proxy: `Caddyfile.deploy`
- Official frontend: `src_frontend`
- Official backend: `src`

## Not Part of This Demo Runtime

The following remain in the repository for legacy, audit or later cleanup, but are not part of the official runtime for this demo:

- `OLD/legacy_stacks/docker-compose.yml`
- `OLD/legacy_stacks/Caddyfile`
- `Web Ailink_Cinema`
- `CINE_AI_PLATFORM`
- `CID_SERVER/automation-engine`
- `automation-engine`
- `n8n`
- `qdrant`

## Required Variables

- `AUTH_SECRET_KEY`: strong, random and secret
- `APP_SECRET_KEY`: required and different from `AUTH_SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: explicitly defined

### Integration Variables Only If Used

- `INTEGRATION_TOKEN_ENCRYPTION_KEY`
- `GOOGLE_DRIVE_OAUTH_STATE_SECRET`
- `GOOGLE_DRIVE_CLIENT_ID`
- `GOOGLE_DRIVE_CLIENT_SECRET`
- `COMFYUI_*` if the demo needs external real render

The placeholders in `.env.home.example` and `.env.vps.example` are not operational. Do not publish or version the real `.env` file.

## What Must Never Be Published

- Real `.env`
- Secrets
- OAuth tokens
- SQLite databases with real data
- Uploaded documents
- User PDFs
- Logs with sensitive data
- Private client outputs

## Safe Startup Flow

```bash
cd /opt/SERVICIOS_CINE

# Home demo
cp .env.home.example .env

# or VPS demo
# cp .env.vps.example .env

# Replace placeholders with strong real secrets before startup
docker compose -f compose.base.yml -f compose.home.yml config
docker compose -f compose.base.yml -f compose.home.yml up -d --build
```

Validate the VPS overlay separately when needed:

```bash
docker compose -f compose.base.yml -f compose.vps.yml config
```

Manual `uvicorn` or `npm run dev` startup remains valid for local development only. It is not the official startup path for this release demo.

## Expected Public and Blocked Routes

Expected public routes:

- `/` -> official React/Vite frontend
- `/cid` -> official React/Vite frontend; real protection happens in the SPA
- `/register/select` -> official React/Vite frontend
- `/legal/privacidad` -> official React/Vite frontend
- `/api/health` -> backend OK
- `/health` -> backend OK

Expected blocked routes:

- `/docs` -> `404`
- `/openapi.json` -> `404`
- `/auth/login` -> `404`
- `/n8n` -> `404`
- `/qdrant` -> `404`
- `/automation` -> `404`

## Minimum Operator Smoke

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

## Demo Organization Label

All demo users are assigned to organizations prefixed with `OFFICIAL DEMO`, for example `OFFICIAL DEMO Org demo_studio`.

The company field displays `OFFICIAL DEMO` instead of a generic demo company label.

Demo credentials must be provisioned out of band. Passwords must not be published in the repository.

## Honest Demo Status

- Apt for controlled commercial demo
- Not public production
- ComfyUI is optional and was not validated in the last smoke
- Queue remains in `memory` mode
- Rate limiter remains basic and in-memory
- TLS/443 remains pending
- Legal review remains pending
- OLD cleanup remains pending

## Historical Notes

- `scripts/smoke_sprint13_rc.py` remains a historical certification reference.
- `scripts/smoke_restart_recovery.py` remains the restart and recovery baseline reference.
- If any older document suggests exposing `/docs`, `/openapi.json` or `/auth/login`, use this guide as the operational source of truth for the current demo.

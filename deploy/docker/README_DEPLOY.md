# AILinkCinema / CID - Deployment Guide

## Quick Start - Local Docker

### Prerequisites
- Docker & Docker Compose installed
- ComfyUI instances running on host (8188, 8189, 8190, 8191)
- `.env` file created from example

### Steps
1. Copy env example:
   ```bash
   cd deploy/docker
   cp .env.local ..
   # Edit .env.local with real secrets
   ```

2. Start services:
   ```bash
   docker compose -f deploy/docker/docker-compose.local.yml up -d
   ```

3. Check health:
   ```bash
   curl http://localhost:8010/health
   ```

4. Access:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8010

5. Stop:
   ```bash
   docker compose -f deploy/docker/docker-compose.local.yml down
   ```

## VPS Deployment

### Prerequisites
- VPS with Docker & Docker Compose
- Domain pointing to VPS
- SSL certificates (Caddy handles auto-SSL)
- ComfyUI instances (external or private network)

### Steps
1. Clone repo on VPS:
   ```bash
   git clone <repo-url>
   cd /srv/ailinkcinema
   ```

2. Create `.env` from example:
   ```bash
   cp deploy/docker/.env.vps.example .env
   nano .env  # Set real secrets and domain
   ```

3. Start with Caddy:
   ```bash
   docker compose -f deploy/docker/docker-compose.vps.yml up -d
   ```

4. Check:
   ```bash
   curl https://your-domain.com/api/health
   ```

## ComfyUI Connection

### Local
- ComfyUI runs on host `127.0.0.1:8188`
- Docker uses `host.docker.internal` or `host-gateway`
- Already configured in `instances.yml` and `.env`

### VPS
- ComfyUI should run on same VPS or private network
- Use `http://host.docker.internal:8188` if on same host
- For separate server, use `http://<internal-ip>:8188`
- **Never expose ComfyUI publicly**

## Volumes & Data
- `ailink_data`: SQLite DB, media assets
- `caddy_data`: SSL certificates
- Backups recommended for production

## What NOT to commit
- `.env` (real secrets)
- `*.db`, `*.db-wal`, `*.db-shm`
- `OLD/` (historical archive)
- `.venv/`, `src/.venv/`
- `scratch/`

## OLD/ Directory
- Historical archive, dead code, old docs
- NOT used in runtime or Docker builds
- Excluded via `.gitignore` and `.dockerignore`
- Keep for reference, do not deploy

## Troubleshooting
- **Backend not starting**: Check logs with `docker compose logs backend`
- **Frontend can't reach API**: Verify `VITE_API_URL` in build args
- **ComfyUI timeout**: Ensure ComfyUI is running and accessible from container
- **DB locked**: Ensure only one process accesses SQLite

## Scripts (Local)
- `scripts/docker_local_up.sh` - Start local stack
- `scripts/docker_local_down.sh` - Stop local stack
- `scripts/docker_local_logs.sh` - View logs
- `scripts/docker_local_health.sh` - Health check

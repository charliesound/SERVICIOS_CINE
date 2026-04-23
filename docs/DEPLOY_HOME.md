# Deploy Home Demo - AILinkCinema

This guide covers deploying AILinkCinema at home with access via Tailscale from a laptop.

## Recommended Topology

- Primary: Docker Tailscale sidecar (`tailscale` + `reverse-proxy-tailscale`) for remote laptop access
- Fallback: Host Tailscale with the existing `compose.home.yml` stack
- ComfyUI remains outside Docker on the home machine and is never exposed publicly

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      HOME NETWORK                        │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │
│  │  Backend   │──▶│   Frontend  │   │   Caddy    │   │
│  │  :8000    │   │  :3000     │   │  :80       │   │
│  └─────┬─────┘   └─────────────┘   └─────────────┘   │
│        │                                         │
│        ▼                                         │
│  ┌─────────────────────────────────────────┐     │
│  │     DOCKER (public_net)                 │     │
│  └─────────────────────────────────────────┘     │
│                                                  │
│  ComfyUI running OUTSIDE Docker:                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │ :8188  │  │ :8189  │  │ :8190  │          │
│  │ Still  │  │ Video  │  │ TTS    │          │
│  └─────────┘  └─────────┘  └─────────┘          │
└──────────────────┬──────────────────────────────┘
                   │ Tailscale
                   ▼
        ┌──────────────────────────────┐
        │      LAPTOP (Client)        │
        │  Access via Tailscale IP   │
        └──────────────────────────────┘
```

## Prerequisites

1. **Docker + Docker Compose** installed on home machine
2. **Tailscale** installed and running on both home machine and laptop
3. **ComfyUI** running locally outside Docker (ports 8188, 8189, 8190, 8191)

## Quick Start

### Primary: Docker + Tailscale Sidecar

```bash
# 1. Copy environment file
cp .env.home.example .env

# 2. Set TS_AUTHKEY in .env

# 3. Start home stack with Tailscale ingress
bash scripts/up_home_tailscale.sh

# 4. Check status
docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml ps
```

### Fallback: Host Tailscale

```bash
# 1. Copy environment file
cp .env.home.example .env

# 2. Start services
bash scripts/up_home_demo.sh

# 3. Check status
docker compose -f compose.base.yml -f compose.home.yml ps
```

## Environment Variables

Key variables in `.env`:

```bash
# Backend
BACKEND_PORT=8000

# ComfyUI on local machine (not Docker)
COMFYUI_BASE_URL=http://host.docker.internal:8188
COMFYUI_STILL=http://host.docker.internal:8188
COMFYUI_VIDEO=http://host.docker.internal:8189
COMFYUI_DUBBING=http://host.docker.internal:8190
COMFYUI_LAB=http://host.docker.internal:8191
```

## Access from Laptop

### Primary: Docker Tailscale Sidecar

1. Get the Tailscale container IP:
   ```bash
   docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml exec tailscale tailscale ip -4
   ```

2. Access from laptop:
   - Demo: `http://<TAILSCALE_CONTAINER_IP>`
   - Health: `http://<TAILSCALE_CONTAINER_IP>/health`
   - Optional MagicDNS: `http://<TS_HOSTNAME>`

### Fallback: Host Tailscale

1. Get your Tailscale IP on the home machine:
   ```bash
   tailscale ip -4
   ```

2. Access from laptop:
   - Backend API: `http://<TAILSCALE_IP>:8000`
   - Frontend: `http://<TAILSCALE_IP>:3000`
   - Health: `http://<TAILSCALE_IP>:8000/health`

## Manual Commands

### Primary: Docker Tailscale Sidecar

```bash
# Build
docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml build

# Start
docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml up -d

# Stop
docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml down

# Logs
docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml logs -f tailscale reverse-proxy-tailscale
```

### Fallback: Host Tailscale

```bash
# Build
docker compose -f compose.base.yml -f compose.home.yml build

# Start
docker compose -f compose.base.yml -f compose.home.yml up -d

# Stop
docker compose -f compose.base.yml -f compose.home.yml down

# View logs
docker compose -f compose.base.yml -f compose.home.yml logs -f

# Restart a service
docker compose -f compose.base.yml -f compose.home.yml restart backend
```

## Smoke Test

Run the smoke test to validate the deployment:

```bash
# Primary ingress path
docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml exec tailscale tailscale ip -4

# Check remote ComfyUI connectivity (from docker network)
docker compose -f compose.base.yml -f compose.home.yml exec backend python scripts/check_remote_comfyui.sh

# Or from host/WSL (recommended for Home Demo)
bash scripts/check_remote_comfyui.sh
```

## ComfyUI Endpoints

### Runtime URLs vs Check URLs

There are **two different contexts** for ComfyUI URLs:

| Context | Used By | Default |
|--------|--------|---------|
| **Runtime** (inside Docker) | Backend containers | `host.docker.internal:PORT` |
| **Check** (from host/WSL) | `check_remote_comfyui.sh` | `localhost:PORT` |
| **Remote ingress** (from laptop) | Tailscale sidecar | `http://<TAILSCALE_CONTAINER_IP>` |

### Core vs Optional Endpoints

For commercial demo, only these are **required**:
- **8188 (Still)**: Image generation - REQUIRED
- **8189 (Video)**: Video generation - REQUIRED

These are **optional** (warning won't block demo):
- **8190 (Dubbing/TTS)**: Voice/tts generation - OPTIONAL
- **8191 (Lab)**: Experimental features - OPTIONAL

### Override Check URLs

To change check URLs from host:

```bash
# Custom URLs for check script
CHECK_COMFYUI_BASE_URL=http://localhost:8188 bash scripts/check_remote_comfyui.sh
CHECK_COMFYUI_VIDEO_URL=http://localhost:8189 bash scripts/check_remote_comfyui.sh

# Require dubbing (normally optional)
REQUIRE_DUBBING=1 bash scripts/check_remote_comfyui.sh
```

### Override Runtime URLs

To change runtime URLs inside Docker:

```bash
# Inside .env for Docker containers
COMFYUI_BASE_URL=http://host.docker.internal:8188
COMFYUI_VIDEO_URL=http://host.docker.internal:8189
COMFYUI_DUBBING=http://host.docker.internal:8190
```

## Troubleshooting

### Backend not starting
- Check Docker is running: `docker ps`
- Check ports available: `netstat -tlnp | grep -E '8000|3000|80'`

### ComfyUI not reachable from Docker
- Verify ComfyUI is running on local machine (NOT in Docker)
- Check ports on host: `curl http://localhost:8188/history`
- The backend in Docker uses `host.docker.internal` to reach the host
- Ensure `extra_hosts` is in compose: `host.docker.internal:host-gateway`

### 8190 (Dubbing) not running
- This is OPTIONAL for demo - won't block startup
- Core features (Still + Video on 8188, 8189) work without it
- Check script shows WARNING but exits successfully

### 8191 (Lab) not running
- This is OPTIONAL for demo - purely informational
- Used only for experimental features

### Tailscale not working
- Primary mode: check the container node
  - `docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml exec tailscale tailscale status`
  - `docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml exec tailscale tailscale ip -4`
- Fallback mode: check the host node
  - `tailscale status`
  - `tailscale ip -4`

### Can't access from laptop
- Primary mode: verify `reverse-proxy-tailscale` is running and shares the Tailscale namespace
- Verify the Tailscale auth key is valid and the node joined the tailnet
- Fallback mode: verify firewall allows inbound connections on the host
- Check Tailscale ACLs if using Tailscale Zero Trust

## Services

| Service | Port | Container | Purpose |
|---------|------|----------|---------|
| backend | 8000 | ailinkcinema_backend | API |
| frontend | 3000 | ailinkcinema_frontend | Web UI |
| reverse-proxy | 80 | ailinkcinema_reverse_proxy | Caddy |
| tailscale | tailnet IP | ailinkcinema_tailscale | Remote ingress namespace |
| reverse-proxy-tailscale | 80 on tailnet | ailinkcinema_reverse_proxy_tailscale | Caddy over Tailscale |

## Networks

- `public_net` (bridge) - Services exposed to outside
- `private_net` (bridge) - Internal communication (future use)

## Next Steps

To migrate to VPS later, see [docs/DEPLOY_VPS.md](DEPLOY_VPS.md) and [docs/ARCHITECTURE_HOME_TO_VPS.md](ARCHITECTURE_HOME_TO_VPS.md).

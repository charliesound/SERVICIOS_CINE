# Architecture: Home to VPS Migration - AILinkCinema

This document explains the architecture differences and migration path between Home demo and VPS deployment.

## Architecture Comparison

| Aspect | Home Demo | VPS |
|--------|----------|-----|
| **Access** | Via Tailscale IP | Via domain (https://ailinkcinema.example.com) |
| **Public IP** | None (Tailscale only) | VPS IP + domain |
| **TLS** | Not required | Caddy with Let's Encrypt |
| **Backend** | SQLite local | SQLite local (or PostgreSQL) |
| **ComfyUI** | host.docker.internal | Via Tailscale to home |
| **Frontend** | Port 3000 | Behind Caddy |

## Key Differences

### Home Demo
```
User (Laptop) 
    │
    ▼ Tailscale
┌────────────────┐
│    HOUSE       │
│  ┌──────────┐ │
│  │ Caddy :80 │ │
│  └────┬─────┘ │
│       │        │
│  ┌───┴───┐   │
│  │Backend│   │
│  │ :8000 │   │
│  └───────┘   │
│       │      │
│  ┌────┴────┐│
│  │Frontend│ │
│  │ :3000  │ │
│  └────────┘ │
└──────┬──────┘
       │
       ▼ ComfyUI outside Docker
┌────────────────┐
│  host machine   │
│  localhost     │
│  :8188        │
└────────────────┘
```

### VPS Deployment
```
User ──▶ Internet ──▶ DNS ──▶ VPS IP
                              │
                         ┌────┴────┐
                         │ Caddy   │
                         │ :80/443 │
                         └────┬────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
               ┌────┴────┐        ┌─────┴─────┐
               │Backend  │        │Frontend  │
               │ :8000  │        │ :3000    │
               └────────┘        └──────────┘
                    │
                    ▼ Tailscale
              ┌────────────────┐
              │    HOUSE      │
              │  ComfyUI     │
              │  :8188      │
              └────────────────┘
```

## What Changes When Migrating

### 1. ComfyUI URLs
**Home (.env)**:
```bash
COMFYUI_BASE_URL=http://host.docker.internal:8188
```

**VPS (.env)**:
```bash
COMFYUI_BASE_URL=http://100.x.x.x:8188  # Tailscale IP of home
```

### 2. Domain/Protocol
**Home**:
```bash
PUBLIC_HOST=localhost
PUBLIC_PROTOCOL=http
```

**VPS**:
```bash
PUBLIC_HOST=ailinkcinema.example.com
PUBLIC_PROTOCOL=https
```

### 3. Caddy Configuration
Home uses basic Caddyfile, VPS uses Caddyfile with TLS.

### 4. Firewall Rules
**Home**: Ports 8000, 3000, 80 via Tailscale only
**VPS**: Ports 80, 443 open (managed by Caddy)

## Migration Steps

### 1. Backup Home Data
```bash
# On home machine
docker exec ailinkcinema_backend tar czf /tmp/ailinkcinema_backup.tar.gz /app/data
docker cp ailinkcinema_backend:/tmp/ailinkcinema_backup.tar.gz ./backup.tar.gz
```

### 2. Transfer to VPS
```bash
# Copy backup to VPS
scp backup.tar.gz vps_user@vps:~/

# On VPS
docker cp ./backup.tar.gz ailinkcinema_backend:/tmp/
docker exec ailinkcinema_backend tar xzf /tmp/backup.tar.gz -C /
```

### 3. Update .env for VPS
Copy `.env.vps.example` to `.env` and update:
- `PUBLIC_HOST` = your domain
- `COMFYUI_BASE_URL` = Tailscale IP of home machine
- All `COMFYUI_*` URLs = Tailscale IPs to home
- `ENABLE_DEMO_ROUTES=0`
- `ENABLE_EXPERIMENTAL_ROUTES=0`
- `ENABLE_POSTPRODUCTION_ROUTES=0`

### 4. Deploy on VPS
```bash
bash scripts/up_vps.sh
```

### 5. Validate
```bash
# Check ComfyUI connectivity
bash scripts/check_remote_comfyui.sh

# Check public access
curl https://ailinkcinema.example.com/health
```

## What Stays the Same

- **Backend code**: Same `src/` container
- **Frontend code**: Same `src_frontend/` container
- **Database**: Same SQLite structure (or use PostgreSQL)
- **Compose overlays**: Uses `compose.base.yml` + `compose.vps.yml`

## ComfyUI Connection Flow

### At Home
```
Docker Network ──▶ host.docker.internal ──▶ localhost:8188
```
- Uses Docker special DNS `host.docker.internal`
- ComfyUI runs outside Docker on same machine

### On VPS
```
VPS Docker ──▶ Tailscale ──▶ Home:8188
```
- VPS connects via Tailscale IP
- ComfyUI stays at home, never exposed publicly
- Tailscale provides encrypted tunnel

## Network Diagrams

### Public vs Private Networks

```yaml
# compose.base.yml defines:
networks:
  public_net:    # Exposed to outside
  private_net:   # Internal only
```

Currently:
- All services use `public_net`
- `private_net` is reserved for future (e.g., PostgreSQL, Redis)

### Security Boundary

```
┌────────────────────────────────────────┐
│          public_net                    │
│  ┌──────────┐ ┌──────────┐           │
│  │ Caddy   │ │Frontend │           │
│  └──────────┘ └──────────┘           │
│         │                          │
│         ▼                          │
│  ┌──────────┐                    │
│  │ Backend │                    │
│  └──────────┘                    │
└────────────────────────────────────────┘
         │
         │ (future: private_net)
         ▼
┌────────────────────────────────────────┐
│         private_net                     │
│  ┌──────────┐ ┌──────────┐           │
│  │   DB    │ │  Redis  │ (future)  │
│  └──────────┘ └──────────┘           │
└────────────────────────────────────────┘
```

## Why This Architecture

### 1. Single Codebase
- Same `src/` and `src_frontend/` for both deployments
- Only compose overlays differ

### 2. ComfyUI Stays Private
- Never exposed to public internet
- Always accessed via Tailscale (encrypted)
- Works the same from home or VPS

### 3. Easy Migration
- Backup → Transfer → Update .env → Deploy
- No code changes needed

### 4. Flexible Networking
- Networks defined in base, can be overridden
- Ready for PostgreSQL/Redis addition

## Checklist for Going Live

- [ ] Backup home data
- [ ] Update DNS A record to VPS IP
- [ ] Set PUBLIC_HOST in .env
- [ ] Set COMFYUI_* URLs to Tailscale IPs
- [ ] Run up_vps.sh
- [ ] Verify health endpoint
- [ ] Check ComfyUI connectivity
- [ ] Test public domain access
- [ ] Update AUTH_SECRET_KEY
- [ ] Enable Caddy basic auth if needed

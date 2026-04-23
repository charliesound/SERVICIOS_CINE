# Deploy VPS - AILinkCinema

This guide covers deploying AILinkCinema on a VPS with public domain access.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      VPS                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │  Backend    │──▶│  Frontend   │   │   Caddy     │     │
│  │  :8000     │   │  :3000      │   │  :80/:443  │     │
│  └─────┬──────┘   └─────────────┘   └─────────────┘     │
│        │                                                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │            DOCKER (public_net)                    │   │
│  └──────────────────────────────────────────────────┘   │
│        │                                                  │
│        │ HTTPS/TLS                                      │
│        ▼                                                  │
│  ┌─────────────────────────────────────┐                │
│  │     PUBLIC INTERNET                 │                │
│  │   https://ailinkcinema.example.com │                │
│  └─────────────────────────────────────┘                │
└────────────────────────────────────────────────────────┘
                          │
                          │ Tailscale (private)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    HOME (ComfyUI)                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │
│  │ :8188   │  │ :8189   │  │ :8190   │                  │
│  │ Still   │  │ Video   │  │ TTS    │                  │
│  └─────────┘  └─────────┘  └─────────┘                  │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **VPS** with Docker + Docker Compose installed
2. **Domain** pointing to VPS IP (via A record)
3. **Tailscale** running on both VPS and home machine
4. **ComfyUI** running at home

## Quick Start

```bash
# 1. Copy VPS environment file
cp .env.vps.example .env

# 2. Edit .env with your domain and Tailscale IP
#    Replace 100.x.x.x with your home machine's Tailscale IP

# 3. Start services
bash scripts/up_vps.sh

# 4. Check status
docker compose -f compose.base.yml -f compose.vps.yml ps
```

## Environment Variables

Key variables in `.env`:

```bash
# Domain
PUBLIC_HOST=ailinkcinema.example.com
PUBLIC_PROTOCOL=https

# ComfyUI via Tailscale (home machine)
COMFYUI_BASE_URL=http://100.x.x.x:8188
COMFYUI_STILL=http://100.x.x.x:8188
COMFYUI_VIDEO=http://100.x.x.x:8189
COMFYUI_DUBBING=http://100.x.x.x:8190
COMFYUI_LAB=http://100.x.x.x:8191
```

## Access

Public access:
- **HTTPS**: `https://ailinkcinema.example.com`
- **API**: `https://ailinkcinema.example.com/api`

## Manual Commands

```bash
# Build
docker compose -f compose.base.yml -f compose.vps.yml build

# Start
docker compose -f compose.base.yml -f compose.vps.yml up -d

# Stop
docker compose -f compose.base.yml -f compose.vps.yml down

# View logs
docker compose -f compose.base.yml -f compose.vps.yml logs -f

# Restart a service
docker compose -f compose.base.yml -f compose.vps.yml restart backend
```

## TLS/SSL

Caddy will automatically generate TLS certificates using Let's Encrypt for your domain. Set:

```bash
CADDY_TLS=internal  # Uses Let's Encrypt
# or
CADDY_TLS=off       # HTTP only (not recommended)
```

## Validate ComfyUI Connection

Check that ComfyUI is reachable from VPS:

```bash
# On VPS
bash scripts/check_remote_comfyui.sh

# Or test manually
curl -I http://<TAILSCALE_IP_HOME>:8188/history
```

## Troubleshooting

### Domain not resolving
- Check DNS A record points to VPS IP
- Wait for propagation (can take up to 24h)
- Test: `nslookup ailinkcinema.example.com`

### TLS not working
- Check port 443 is open in firewall
- Check Caddy is generating certs: `docker logs ailinkcinema_reverse_proxy`

### ComfyUI not reachable
- Verify Tailscale is running on home machine
- Check home firewall allows port 8188-8191
- Test from VPS: `curl http://<TAILSCALE_IP_HOME>:8188/history`

### Backend errors
- Check logs: `docker logsailinkcinema_backend`
- Verify DATABASE_URL is set correctly

## Services

| Service | Port | Container | Purpose |
|---------|------|----------|---------|
| backend | 8000 | ailinkcinema_backend | API |
| frontend | 3000 | ailinkcinema_frontend | Web UI |
| reverse-proxy | 80/443 | ailinkcinema_reverse_proxy | Caddy + TLS |

## Networks

- `public_net` (bridge) - Services exposed to outside
- `private_net` - Internal communication (future use)

## Moving from Home to VPS

To migrate from Home demo to VPS:

1. **Backup data**:
   ```bash
   # On home
   docker execailinkcinema_backend tar czf /tmp/backup.tar.gz /app/data
   docker cpailinkcinema_backend:/tmp/backup.tar.gz ./backup.tar.gz
   ```

2. **Transfer**:
   ```bash
   # Copy to VPS
   scp backup.tar.gz vps:~/

   # Restore
   docker cp ./backup.tar.gzailinkcinema_backend:/tmp/
   docker execailinkcinema_backend tar xzf /tmp/backup.tar.gz -C /app/data
   ```

3. **Update .env** with new COMFYUI URLs (Tailscale IPs may differ)

## Security Checklist

- [ ] Change AUTH_SECRET_KEY to strong random value
- [ ] Enable Caddy basic auth if needed
- [ ] Set CADDY_BASIC_AUTH_PASSWORD_HASH
- [ ] Configure firewall (only ports 80, 443)
- [ ] Use strong DATABASE_URL password if using PostgreSQL
- [ ] Enable Tailscale ACLs for ComfyUI access

## See Also

- [docs/ARCHITECTURE_HOME_TO_VPS.md](ARCHITECTURE_HOME_TO_VPS.md) - Migration guide
- [docs/DEPLOY_HOME.md](DEPLOY_HOME.md) - Home demo setup
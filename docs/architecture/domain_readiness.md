# CID.INFRA.DOMAIN.READINESS.1 — Diseño de dominio, subdominios y arquitectura local/VPS

## 1. Infraestructura actual auditada

| Servicio | Container | Puerto interno | Puerto host | Expuesto públicamente |
|---|---|---|---|---|
| Backend | `ailinkcinema_backend` | 8000 | **127.0.0.1:8000** | No (corregido en CID.INFRA.DOMAIN.CONFIG.1) |
| Frontend | `ailinkcinema_frontend` | 80 | — | No directo |
| Reverse proxy | `ailinkcinema_reverse_proxy` | 80 | **127.0.0.1:80** | No (corregido en CID.INFRA.DOMAIN.CONFIG.1) |
| PostgreSQL | `ailinkcinema_postgres` | 5432 | 127.0.0.1:5432 | No |
| Qdrant | `ailinkcinema_qdrant` | 6333 | 127.0.0.1:6333 | No |
| n8n | `ailinkcinema_n8n` | 5678 | 127.0.0.1:5678 | No |
| Ollama | `ailinkcinema_ollama` | 11434 | 127.0.0.1:11434 | No |
| ComfyUI | `servicios_cine-comfyui-still-1` | 8188 | — | Exited |
| Flowise | ❌ No existe | — | — | — |

### Redes Docker

| Red | Nombre real | Contenedores |
|---|---|---|
| `public_net` | `ailinkcinema_public` (172.23.0.0/16) | backend, frontend, reverse-proxy |
| `private_net` | `ailinkcinema_private` (172.20.0.0/16) | backend, qdrant, ollama |

### Reverse proxy actual (Caddyfile.deploy)
- Solo HTTP en puerto 80
- Sin TLS/HTTPS configurado (`auto_https disable_redirects`)
- Sin nombres de dominio — solo responde en `:80`
- Bloquea `/n8n`, `/qdrant`, `/auth`, `/docs`
- Todo lo demás → frontend React

### Frontend
- `VITE_API_URL` → `/api` (proxy inverso)
- `VITE_COMFY_URL` → `http://localhost:8188`
- `VITE_SITE_URL` → opcional (SEO)

### Variables de dominio existentes
- `PUBLIC_HOST` → `ailinkcinema.example.com` (tanto en `.env.vps.example` como en `.env.home.example`)
- `PUBLIC_PROTOCOL` → `https`
- `CUSTOM_DOMAIN` → `ailinkcinema.example.com`
- `frontend_base_url` (Python config) → `http://localhost:3000`

### Riesgos actuales
1. ~~**Backend expuesto en 0.0.0.0:8010** — cualquiera en la red local puede alcanzar la API directamente sin pasar por el reverse proxy~~ ✅ **RESUELTO** en `CID.INFRA.DOMAIN.CONFIG.1`. Backend bind a `127.0.0.1:8000`.
2. **Sin TLS** — Caddyfile tiene `auto_https disable_redirects`. Cloudflare Tunnel (CID.INFRA.DOMAIN.TUNNEL.1) provee TLS automático.
3. ~~**CORS permisivo** — `cors_allowed_origins` permite `*` en development~~ ✅ **RESUELTO** en `CID.INFRA.DOMAIN.CONFIG.1`. Ahora configurable vía env var con field_validator en `src/core/config.py`.
4. **ComfyUI no corre en stack** — el contenedor still salió con error
5. **Flowise no existe** — no hay compose, no hay imagen, no hay configuración
6. **Sin separación de subdominios** — todo en un solo `:80`

## 2. Subdominios propuestos

| Subdominio | Servicio | Público | Auth | Notas |
|---|---|---|---|---|
| `app.tudominio.com` | Frontend React | Sí | JWT (existente) | Interfaz principal CID |
| `api.tudominio.com` | Backend FastAPI | Sí | JWT + API key | Endpoints REST |
| `demo.tudominio.com` | Frontend (demo mode) | Sí | Público limitado | Demos para clientes |
| `n8n.tudominio.com` | n8n | Sí* | n8n auth + SSO | Automatizaciones |
| `flowise.tudominio.com` | Flowise | Sí* | Flowise auth | Agentes/RAG visual |
| `gpu.tudominio.com` | GPU worker (túnel) | No | VPN/túnel | Solo desde VPS |
| `comfy.tudominio.com` | ComfyUI (túnel) | No | VPN/túnel | Solo desde VPS |
| `ollama.tudominio.com` | Ollama (túnel) | No | VPN/túnel | Solo desde VPS |

\* `n8n.tudominio.com` y `flowise.tudominio.com` son públicos solo tras autenticación fuerte. Idealmente tras Cloudflare Access / Authentik / Authelia.

## 3. Arquitectura local demo (fase inmediata)

```
                    ┌──────────────────────┐
                    │  Cloudflare Tunnel    │
                    │  o Tailscale Funnel   │
                    │  tunel.tudominio.com  │
                    └──────────┬───────────┘
                               │ TLS (automático)
                    ┌──────────▼───────────┐
                    │  Caddy reverse-proxy  │
                    │  (localhost:80)       │
                    │  sin TLS directo      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Backend :8000        │
                    │  Frontend :80         │
                    │  (docker compose)     │
                    └──────────────────────┘
```

### Principios local demo
- Backend y frontend solo accesibles por reverse proxy
- Backend bind a `127.0.0.1:8000` (no 0.0.0.0)
- Reverse proxy bind a `127.0.0.1:80` + túnel externo
- PostgreSQL, Qdrant, Ollama, n8n bind a `127.0.0.1` (ya correcto)
- Túnel (Cloudflare Tunnel o Tailscale Funnel) maneja TLS automáticamente

### Cambio mínimo necesario para local demo (✅ aplicado en CID.INFRA.DOMAIN.CONFIG.1)

Los siguientes cambios ya están en producción (`47a0ba1`):

```yaml
# compose.home.yml — backend bind 127.0.0.1:8000
backend:
    ports:
      - "127.0.0.1:${BACKEND_PORT:-8000}:8000"
```

```yaml
# compose.base.yml — reverse proxy bind 127.0.0.1:80
reverse-proxy:
    ports:
      - "127.0.0.1:${HTTP_PORT:-80}:80"
```

### Variables .env.local.demo (para usar con tunnel)

```ini
# Dominio
PUBLIC_HOST=tunel.tudominio.com
PUBLIC_PROTOCOL=https

# Backend (solo localhost)
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

# CORS para tráfico por túnel
CORS_ALLOWED_ORIGINS=https://tunel.tudominio.com

# URLs internas (servicios Docker)
QDRANT_URL=http://qdrant:6333
OLLAMA_URL=http://ollama:11434
N8N_URL=http://n8n:5678

# GPU local
GPU_WORKER_MODE=local
COMFYUI_BASE_URL=http://host.docker.internal:8188
```

## 4. Arquitectura VPS + GPU worker local RTX 5090 (fase futura)

```
                    ┌──────────────────────────────────┐
                    │        Cloudflare (DNS + CDN)      │
                    │  app.tudominio.com                │
                    │  api.tudominio.com                │
                    │  n8n.tudominio.com                │
                    │  flowise.tudominio.com            │
                    └──────────────┬───────────────────┘
                                   │ TLS (Cloudflare)
                    ┌──────────────▼───────────────────┐
                    │   VPS (servidor cloud)             │
                    │                                   │
                    │   Caddy (reverse proxy)            │
                    │   ├── app.tudominio.com → frontend │
                    │   ├── api.tudominio.com → backend  │
                    │   ├── n8n.tudominio.com → n8n     │
                    │   └── flowise.tudominio.com →      │
                    │                flowise             │
                    │                                   │
                    │   PostgreSQL :5432 (127.0.0.1)     │
                    │   Qdrant :6333 (127.0.0.1)         │
                    │   n8n :5678 (127.0.0.1)            │
                    │   Flowise :3000 (127.0.0.1)        │
                    └──────┬────────────────────────────┘
                           │ Tailscale / WireGuard
                    ┌──────▼────────────────────────────┐
                    │   PC local (RTX 5090, 32GB VRAM)   │
                    │                                   │
                    │   ComfyUI (8188-8192)             │
                    │   ├── still :8188                 │
                    │   ├── video :8189                 │
                    │   ├── dubbing :8190               │
                    │   ├── restoration :8191           │
                    │   └── 3D :8192                    │
                    │                                   │
                    │   Ollama :11434                   │
                    │   (nomic-embed-text, llama3.2,     │
                    │    qwen2.5, etc.)                  │
                    │                                   │
                    │   GPU worker API (custom)         │
                    └──────────────────────────────────┘
```

### Principios VPS + GPU worker
- VPS: servicios ligeros (backend, frontend, DB, Qdrant, n8n, Flowise)
- PC local RTX 5090: GPU-bound (ComfyUI, Ollama, workers IA)
- Comunicación VPS ↔ PC local por Tailscale (WireGuard nativo, NAT traversal)
- GPU services NO expuestos públicamente — solo reachable vía Tailscale IP
- Backend en VPS conecta a GPU worker vía `http://100.x.x.x:port` (Tailscale)

### Variables .env.vps

```ini
# ===== DOMINIOS PÚBLICOS =====
PUBLIC_APP_URL=https://app.tudominio.com
PUBLIC_API_URL=https://api.tudominio.com
PUBLIC_DEMO_URL=https://demo.tudominio.com
PUBLIC_N8N_URL=https://n8n.tudominio.com
PUBLIC_FLOWISE_URL=https://flowise.tudominio.com

# ===== CORS =====
CORS_ALLOWED_ORIGINS=https://app.tudominio.com,https://demo.tudominio.com

# ===== INTERNAL (Docker compose) =====
DATABASE_URL=postgresql+asyncpg://ailinkcinema:****@postgres:5432/ailinkcinema
QDRANT_URL=http://qdrant:6333
N8N_URL=http://n8n:5678
FLOWISE_URL=http://flowise:3000

# ===== GPU WORKER (Tailscale) =====
GPU_WORKER_MODE=remote
GPU_WORKER_BASE_URL=http://100.x.x.x  # Tailscale IP del PC local

COMFYUI_STILL_BASE_URL=http://100.x.x.x:8188
COMFYUI_VIDEO_BASE_URL=http://100.x.x.x:8189
COMFYUI_DUBBING_BASE_URL=http://100.x.x.x:8190
COMFYUI_RESTORATION_BASE_URL=http://100.x.x.x:8191
COMFYUI_3D_BASE_URL=http://100.x.x.x:8192
OLLAMA_BASE_URL=http://100.x.x.x:11434
```

## 5. Recomendación de túnel/red

| Opción | Local demo | VPS futuro | Voto |
|---|---|---|---|
| **Cloudflare Tunnel** | `cloudflared tunnel --url localhost:80` | DNS + Tunnel para subdominios | ⭐ **Recomendado** |
| **Tailscale Funnel** | `tailscale funnel 80` | Tailscale para GPU worker | ✅ Adicional |
| **WireGuard manual** | Complejo | VPS ↔ PC GPU worker | ✅ Alternativa |

### Cloudflare Tunnel (recomendado para local demo)
```bash
# Instalar cloudflared
docker run -d --name cloudflared \
  cloudflare/cloudflared:latest tunnel --no-autoupdate \
  --url http://host.docker.internal:80

# O desde el PC:
cloudflared tunnel --url http://localhost:80
```
- ✅ TLS automático
- ✅ Sin puertos abiertos en firewall
- ✅ Subdominios vía Cloudflare DNS
- ⚠️ Límite 100 MB en plan gratuito (suficiente para demo)

### Tailscale (recomendado para VPS ↔ GPU worker)
- ✅ WireGuard nativo
- ✅ NAT traversal (no requiere puertos abiertos)
- ✅ MagicDNS para resolución de nombres
- ✅ Ya hay un `compose.home.tailscale.yml` existente
- ⚠️ GPU worker necesita Tailscale instalado en Windows

## 6. Caddyfile propuesto (futuro VPS)

```caddy
app.tudominio.com {
    reverse_proxy frontend:80
}

api.tudominio.com {
    reverse_proxy backend:8000
}

n8n.tudominio.com {
    reverse_proxy n8n:5678
}

flowise.tudominio.com {
    reverse_proxy flowise:3000
}
```

## 7. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Backend expuesto en 0.0.0.0:8010 | Cualquiera en LAN accede a la API | Cambiar a 127.0.0.1 |
| Sin TLS en demo local | Tráfico sin cifrar si se expone | Cloudflare Tunnel o Caddy con Let's Encrypt |
| CORS con `*` en producción | CSRF, fuga de datos | Restringir a dominios específicos vía env |
| n8n sin auth en expuesto | RCE, fuga de workflows | n8n requiere login + proxy bloquea por defecto |
| ComfyUI sin auth si expuesto | Uso no autorizado de GPU | Solo accesible vía Tailscale |
| Flowise no existe | Roadblock para agentes RAG | Agregar compose cuando se diseñe |

## 8. Plan por fases

| Fase | Descripción | Cambios | Dependencias |
|---|---|---|---|
| **CID.INFRA.DOMAIN.CONFIG.1** | Bind backend y proxy a 127.0.0.1, CORS por env, alinear .env.example | compose.home.yml, compose.base.yml, .env | Ninguna |
| ~~**CID.INFRA.TUNNEL.LOCAL.1**~~→ **CID.INFRA.DOMAIN.TUNNEL.1** | ✅ Docs y plantilla cloudflared creados. Pendiente: dominio, Cloudflare account, token real. | `docs/ops/cloudflare_tunnel_setup.md`, `infra/cloudflare/cloudflared.example.yml` | Dominio comprado |
| **CID.INFRA.VPS.PROVISION.1** | Desplegar en VPS con subdominios + TLS | compose.vps.yml, Caddyfile.vps, CI/CD | Dominio, VPS contratado |
| **CID.INFRA.GPU.TAILSCALE.1** | Conectar GPU worker local RTX 5090 al VPS vía Tailscale | .env.vps, Tailscale en Windows | CID.INFRA.VPS.PROVISION.1 |
| **CID.INFRA.FLOWISE.ADD.1** | Agregar Flowise al stack VPS | compose.flowise.yml, Caddyfile | CID.INFRA.VPS.PROVISION.1 |

## 9. Cambios aplicados (CID.INFRA.DOMAIN.CONFIG.1 + CID.DB.POSTGRES.RUNTIME.SWITCHOVER.1)

| # | Cambio | Archivo | Commit |
|---|---|---|---|
| 1 | Reverse proxy bind a 127.0.0.1 | `compose.base.yml:82` | `47a0ba1` |
| 2 | Backend bind a 127.0.0.1, ports a 8000 | `compose.home.yml:11` | `47a0ba1` |
| 3 | BACKEND_HOST=127.0.0.1, CORS_ALLOWED_ORIGINGS env var | `.env.example`, `src/core/config.py` | `47a0ba1` |
| 4 | DATABASE_URL a PostgreSQL + asyncpg server_settings | `compose.home.yml:33`, `src/database.py:62` | `47a0ba1` |
| 5 | Qdrant movido a private_net con DNS interno | Docker compose overlays | `CID.RAG.QDRANT.NETWORK.PORTABLE.1` |

## 10. GO/NO-GO

| Fase | Estado |
|---|---|
| **CID.INFRA.DOMAIN.CONFIG.1** | ✅ **GO — aplicado** (commit `47a0ba1`, tag `cid-dev-stable-postgres-runtime-switchover-20260531`) |
| **CID.INFRA.DOMAIN.TUNNEL.1** | ✅ **GO — documentación completa** (commit `98e70a5`, tag `cid-dev-stable-cloudflare-tunnel-docs-20260531`) |
| **CID.INFRA.VPS.PROVISION.1** | ⏳ Pendiente |
| **CID.INFRA.GPU.TAILSCALE.1** | ⏳ Pendiente |
| **CID.INFRA.FLOWISE.ADD.1** | ⏳ Pendiente |

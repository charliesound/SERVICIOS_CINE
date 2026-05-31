# CID.INFRA.DOMAIN.TUNNEL.1 — Cloudflare Tunnel Setup for AILinkCinema/CID

## 1. Architecture

```
                          Internet
                             │
                    ┌────────▼────────┐
                    │  Cloudflare DNS  │
                    │  + CDN + TLS     │
                    │  (automático)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Cloudflare Tunnel │
                    │  (cloudflared)    │
                    │  conecta a        │
                    │  127.0.0.1:80     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Caddy reverse    │
                    │ proxy            │
                    │ 127.0.0.1:80     │
                    └──┬──────────┬───┘
                       │          │
              ┌────────▼──┐  ┌───▼────────┐
              │ Frontend   │  │ Backend     │
              │ :80        │  │ :8000       │
              │ React SPA  │  │ FastAPI     │
              └────────────┘  └─────────────┘
```

### Principios

- **Cloudflare Tunnel** es el único punto de entrada externo.
- **No se abren puertos en el firewall** — cloudflared hace conexión saliente a Cloudflare.
- **TLS automático** — Cloudflare maneja los certificados.
- **Caddy en `127.0.0.1:80`** — solo accesible localmente y por cloudflared.
- **Backend en `127.0.0.1:8000`** — solo accesible por Caddy, no expuesto directamente.
- **Servicios internos (PostgreSQL, Qdrant, Ollama, ComfyUI, n8n)** — bind a `127.0.0.1`, no pasan por el túnel.

## 2. Servicios que SÍ pueden pasar por el túnel

| Subdominio | Servicio real | Puerto local | Notas |
|---|---|---|---|
| `app.tudominio.com` | Frontend React (SPA) | → Caddy `:80` → `frontend:80` | Interfaz principal de CID |
| `api.tudominio.com` | Backend FastAPI | → Caddy `:80/api/*` → `backend:8000` | Endpoints REST. JWT requerido |
| `demo.tudominio.com` | Frontend (demo mode) | → Caddy `:80` → `frontend:80` | Mismo frontend, sin auth |

### Recomendación de routing

**Cloudflare Tunnel → Caddy reverse proxy (`127.0.0.1:80`) → frontend/backend**

- `api.tudominio.com` NO debe ir directo al backend (`127.0.0.1:8000`) porque:
  - Se perderían los security headers de Caddy (`X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`).
  - Mayor superficie de ataque al exponer FastAPI directamente.
  - El backend no debe saber de dominios externos.
- `app.tudominio.com` y `demo.tudominio.com` apuntan al mismo Caddy `:80`.
  - La diferenciación entre app y demo se hace a nivel de aplicación (flag `DEMO_ENABLED`).

## 3. Servicios que NO deben exponerse

| Servicio | Puerto | Motivo |
|---|---|---|
| **PostgreSQL** | 5432 | Base de datos con todos los datos de CID. Nunca expuesta. |
| **Qdrant** | 6333, 6334 | Vectores de búsqueda semántica. Solo uso interno del backend. |
| **Ollama** | 11434 | LLM local. Sin auth. Uso no autorizado = costo/riesgo. |
| **ComfyUI** | 8188-8192 | GPU rendering. Sin auth. Uso no autorizado agota VRAM. |
| **n8n** | 5678 | Automatizaciones. Riesgo de RCE si se expone sin auth fuerte. |
| **Redis** (futuro) | 6379 | Caché/cola. Sin auth por defecto. |

Estos servicios están bind a `127.0.0.1` y NO deben tener entrada en el tunnel ingress.

## 4. Requisitos previos

- [ ] Dominio propio (ej. `tudominio.com`) comprado y apuntando a Cloudflare Nameservers.
- [ ] Cuenta Cloudflare (plan gratuito suficiente para demo).
- [ ] Docker y docker compose funcionando en el host.
- [ ] Backend y reverse proxy bind a `127.0.0.1` (ya implementado en `47a0ba1`).
- [ ] `.env` configurado con `BACKEND_HOST=127.0.0.1`.

## 5. Pasos para crear el túnel

### 5.1. En Cloudflare Dashboard

1. Ir a **Cloudflare Dashboard** → **Zero Trust** → **Networks** → **Tunnels**.
2. Crear tunnel → darle nombre (ej. `cid-production` o `ailinkcinema-local`).
3. Cloudflare genera un `TUNNEL_ID` y un `TUNNEL_TOKEN`.
4. Elegir `cloudflared` como connector (no Docker).
5. Descargar el JSON con el token o copiar el token directamente.

### 5.2. Configurar cloudflared en el host

Opción A — Docker (recomendada):

```bash
docker run -d --name cloudflared \
  --restart unless-stopped \
  --network host \
  cloudflare/cloudflared:latest tunnel run \
  --token eyJ...token-aqui...
```

Opción B — cloudflared binary:

```bash
# Instalar
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Autenticar (abre navegador)
cloudflared tunnel login

# Crear tunnel
cloudflared tunnel create cid-production
# → Crea ~/.cloudflared/<TUNNEL_ID>.json
# → Muestra TUNNEL_ID

# Routing DNS
cloudflared tunnel route dns cid-production app.tudominio.com
cloudflared tunnel route dns cid-production api.tudominio.com
cloudflared tunnel route dns cid-production demo.tudominio.com
```

### 5.3. Configurar ingress

Copiar `infra/cloudflare/cloudflared.example.yml` a `~/.cloudflared/config.yml` y ajustar el TUNNEL_ID y credentials-file.

```yaml
tunnel: CID_TUNNEL_ID
credentials-file: /home/USER/.cloudflared/CID_TUNNEL_ID.json

ingress:
  - hostname: app.tudominio.com
    service: http://127.0.0.1:80
  - hostname: api.tudominio.com
    service: http://127.0.0.1:80
  - hostname: demo.tudominio.com
    service: http://127.0.0.1:80
  - service: http_status:404
```

### 5.4. Iniciar cloudflared

```bash
# Validar sintaxis
cloudflared tunnel validate

# Iniciar
cloudflared tunnel run cid-production

# O como servicio
cloudflared service install
sudo systemctl start cloudflared
sudo systemctl status cloudflared
```

### 5.5. Verificar

```bash
# El túnel debe mostrar connected
cloudflared tunnel info cid-production

# Probar desde internet (o usando curl con el Host header)
curl -s -H "Host: app.tudominio.com" http://127.0.0.1:80 | head -5
curl -s -H "Host: api.tudominio.com" http://127.0.0.1:80/api/health
curl -s -H "Host: demo.tudominio.com" http://127.0.0.1:80 | head -5
```

## 6. DNS en Cloudflare

### Mediante cloudflared CLI (automático)

```bash
cloudflared tunnel route dns cid-production app.tudominio.com
cloudflared tunnel route dns cid-production api.tudominio.com
cloudflared tunnel route dns cid-production demo.tudominio.com
```

### Manual en Cloudflare Dashboard

Si se prefiere crear los DNS records manualmente:

| Tipo | Nombre | Contenido | Proxy |
|---|---|---|---|
| CNAME | `app` | `<TUNNEL_ID>.cfargotunnel.com` | ✅ Proxied (orange cloud) |
| CNAME | `api` | `<TUNNEL_ID>.cfargotunnel.com` | ✅ Proxied |
| CNAME | `demo` | `<TUNNEL_ID>.cfargotunnel.com` | ✅ Proxied |

> ⚠️ Todos deben tener el proxy naranja (proxied) para que Cloudflare Tunnel funcione.

## 7. Consideraciones de seguridad

### CORS

Actualizar `CORS_ALLOWED_ORIGINS` en `.env`:

```ini
CORS_ALLOWED_ORIGINS=https://app.tudominio.com,https://demo.tudominio.com
```

### n8n (si se expone en el futuro)

- n8n solo debe exponerse tras Cloudflare Access o con autenticación fuerte.
- No incluir n8n en el ingress sin configurar auth previamente.

### Rate limiting

Cloudflare plan gratuito incluye protección DDoS básica y WAF. Para rate limiting avanzado:

- Usar Cloudflare Rate Limiting Rules (disponible en plan gratuito con límites).
- Alternativamente, mantener rate limit por backend (`LOGIN_RATE_LIMIT_PER_MINUTE` en `.env`).

## 8. Validación post-despliegue

- [ ] `cloudflared tunnel list` muestra el tunnel como `HEALTHY`.
- [ ] `curl -s https://app.tudominio.com` devuelve el HTML del frontend.
- [ ] `curl -s https://api.tudominio.com/api/health` devuelve `200 OK`.
- [ ] Login funcional desde `https://app.tudominio.com`.
- [ ] CORS configurado correctamente (sin errores en consola del navegador).
- [ ] `https://api.tudominio.com/docs` → debe responder `404` (bloqueado por Caddy).
- [ ] `https://api.tudominio.com/n8n` → debe responder `404`.
- [ ] `https://api.tudominio.com/qdrant` → debe responder `404`.
- [ ] Servicios internos NO accesibles desde internet:
  - `https://app.tudominio.com:5432` → timed out
  - `https://app.tudominio.com:6333` → timed out
  - `https://api.tudominio.com:11434` → timed out
- [ ] `curl -s https://app.tudominio.com/health` devuelve estado del backend.
- [ ] TLS activo (Cloudflare emite certificado automáticamente).

## 9. Rollback

### Opción A — Desactivar DNS (rápido)

En Cloudflare Dashboard:
1. Ir a **DNS** → **Records**.
2. Cambiar los registros CNAME de `app`, `api`, `demo` de proxied (orange) a DNS only (grey).
3. El tráfico dejará de llegar al tunnel.

### Opción B — Detener cloudflared

```bash
# Docker
docker stop cloudflared
docker rm cloudflared

# Binary
sudo systemctl stop cloudflared
# o
kill $(pgrep cloudflared)
```

### Opción C — Eliminar tunnel

```bash
cloudflared tunnel delete cid-production
```

Luego en Cloudflare Dashboard:
- Ir a **Zero Trust** → **Networks** → **Tunnels**.
- Eliminar el tunnel.
- Eliminar los DNS records CNAME (o dejarlos apuntando a DNS only).

## 10. Diferencias entre local demo y VPS

| Aspecto | Local demo (esta fase) | VPS futuro |
|---|---|---|
| Tunnel origen | PC local con Docker | VPS cloud |
| GPU | RTX 5090 local (ComfyUI+Ollama) | No GPU — remota vía Tailscale |
| cloudflared | Docker container o binary | Binary como servicio |
| n8n exposición | No recomendado | Sí, tras Cloudflare Access |
| Flowise | No existe | Sí, en VPS |
| TLS | Cloudflare Tunnel (automático) | Cloudflare Tunnel o Caddy Let's Encrypt |
| Caddy TLS | No necesario (`auto_https disable_redirects`) | Opcional si se usa directo |

## 11. Archivos de referencia

- [`infra/cloudflare/cloudflared.example.yml`](../infra/cloudflare/cloudflared.example.yml) — Plantilla de configuración cloudflared.
- [`docs/architecture/domain_readiness.md`](../architecture/domain_readiness.md) — Diseño de arquitectura de dominios.
- [`Caddyfile.deploy`](../../Caddyfile.deploy) — Configuración del reverse proxy.
- [`compose.base.yml`](../../compose.base.yml) — Servicios base (reverse proxy bind a 127.0.0.1).
- [`compose.home.yml`](../../compose.home.yml) — Override home (backend bind a 127.0.0.1).

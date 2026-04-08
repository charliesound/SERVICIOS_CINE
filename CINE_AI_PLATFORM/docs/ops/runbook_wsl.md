# Runbook WSL (operacion real)

## Alcance
Operacion diaria del despliegue actual en servidor casero Windows + WSL para este repo.

## Referencias reales del repo
- Compose: `deploy/docker-compose.wsl.yml`
- Compose auth demo opcional: `deploy/docker-compose.wsl.demo-auth.yml`
- Nginx runtime: `infra/nginx/default.conf`
- Nginx con auth basica demo: `infra/nginx/default.auth.conf`
- API image/runtime: `apps/api/Dockerfile`
- Web image/runtime: `apps/web/Dockerfile`
- Variables base: `.env.compose.example`
- Perfil remoto demo: `deploy/.env.demo.example`
- Estrategia de acceso remoto: `docs/ops/remote_access_strategy.md`
- Operativa demo remota: `docs/ops/demo_remote_mode.md`
- Checklist preflight: `docs/ops/demo_preflight_checklist.md`
- Recovery rapido: `docs/ops/demo_failure_recovery.md`
- Auth basica proxy (opcional): `docs/security/demo_proxy_basic_auth.md`
- Estado operativo: `docs/ops/operational_status.md`
- Smoke remoto rapido: `docs/ops/demo_smoke_flow.md`
- Smoke render minimo: `docs/ops/demo_render_smoke.md`
- Retencion/limpieza render jobs: `docs/ops/render_jobs_retention.md`

## Pre requisitos
- Windows 11 + WSL2
- Docker Desktop con integracion WSL activa
- Repo en disco accesible desde WSL

## Ruta recomendada en WSL
- Recomendada: `/home/<usuario>/srv/CINE_AI_PLATFORM`
- Evitar rutas montadas lentas de Windows para ejecucion diaria (`/mnt/c/...`) cuando sea posible.

## Preparacion inicial (una sola vez)
Desde la raiz del repo:

```bash
cp .env.compose.example .env.compose
```

Editar `.env.compose` segun entorno:
- `WEB_PORT_BIND=8080`
- `CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080`
- `COMFYUI_BASE_URL=http://host.docker.internal:8188`
- `ENABLE_LEGACY_ROUTES=false` para modo servidor recomendado

## Modo remoto (demo fuera de casa)
Desde la raiz del repo:

```bash
cp deploy/.env.demo.example .env.demo
```

Configurar `.env.demo` segun canal remoto elegido:
- Tailscale: `CORS_ORIGINS=http://<host-tailnet>:8080`
- Cloudflare Tunnel: `CORS_ORIGINS=https://<demo-domain>`

Arranque remoto:

```bash
docker compose --env-file .env.demo -f deploy/docker-compose.wsl.yml up -d --build
```

Arranque remoto con auth basica en proxy (opcional):

```bash
bash scripts/demo_start.sh --env .env.demo --with-basic-auth
```

## Arranque
Desde la raiz del repo:

```bash
docker compose --env-file .env.compose -f deploy/docker-compose.wsl.yml up -d --build
```

## Parada

```bash
docker compose --env-file .env.compose -f deploy/docker-compose.wsl.yml down
```

## Reinicio

```bash
docker compose --env-file .env.compose -f deploy/docker-compose.wsl.yml restart
```

## Estado y logs
- Estado servicios:

```bash
docker compose --env-file .env.compose -f deploy/docker-compose.wsl.yml ps
```

- Logs API:

```bash
docker compose --env-file .env.compose -f deploy/docker-compose.wsl.yml logs -f api
```

- Logs Web/Nginx:

```bash
docker compose --env-file .env.compose -f deploy/docker-compose.wsl.yml logs -f web
```

- Logs de todo el stack:

```bash
docker compose --env-file .env.compose -f deploy/docker-compose.wsl.yml logs -f
```

Wrapper recomendado de logs en demo:

```bash
bash scripts/demo_logs.sh --env .env.demo
```

## Verificacion operativa rapida
- Frontend: `http://localhost:8080`
- Health API via nginx: `http://localhost:8080/api/health`
- Health API detalle: `http://localhost:8080/api/health/details`
- Config API: `http://localhost:8080/api/config`

## Comprobar conectividad ComfyUI (desde backend)
Si ComfyUI esta caido, este check no debe tumbar la API:

```bash
curl -s http://localhost:8080/api/health/details
```

Revisar `health.integrations.comfyui`:
- `configured: true|false`
- `reachable: true|false`
- `error` (solo si falla)

Estado operativo resumido:

```bash
curl -s http://localhost:8080/api/ops/status
```

## Separacion Docker vs ComfyUI
- Docker Compose levanta solo `api` y `web`.
- ComfyUI no forma parte de `deploy/docker-compose.wsl.yml`.
- Backend consulta ComfyUI por HTTP usando `COMFYUI_BASE_URL`.
- Si ComfyUI cae, la API sigue viva; el estado se refleja en `/api/health/details`.
- Nunca abrir ComfyUI en Cloudflare Tunnel ni en endpoints publicos.

## Uso en demos remotas (laptop + hotspot del movil)
Escenario: servidor en laptop Windows, asistentes conectados al mismo hotspot.

1. Conecta la laptop al hotspot del movil.
2. Identifica IP IPv4 de la laptop en esa red (PowerShell):

```powershell
ipconfig
```

3. Asegura `WEB_PORT_BIND=8080` en `.env.compose`.
4. Ajusta CORS API en `.env.compose` para incluir la IP de demo, por ejemplo:
   - `CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://192.168.43.120:8080`
5. Levanta stack con el comando de arranque.
6. Comparte URL de demo: `http://<IP_LAPTOP>:8080`
7. Mantener ComfyUI sin exposicion publica (solo endpoint privado para backend).

## Acceso remoto seguro recomendado
- Principal: Tailscale (solo equipo interno).
- Alternativa para invitados: Cloudflare Tunnel + Cloudflare Access.
- Detalle operativo: `docs/ops/remote_access_strategy.md`.

## Checklist pre-demo
- [ ] `docker compose ... ps` muestra `api` y `web` en estado `Up`
- [ ] `http://localhost:8080` responde
- [ ] `http://localhost:8080/api/health` responde `ok: true`
- [ ] `http://localhost:8080/api/health/details` responde (aunque ComfyUI no este reachable)
- [ ] `CORS_ORIGINS` incluye origen local y origen de demo por IP
- [ ] Firewall de Windows permite entrada al puerto `8080` en red privada
- [ ] Backup reciente de `apps/api/data` antes de la demo

## Scripts operativos recomendados
- preflight:

```bash
bash scripts/demo_preflight.sh --env .env.demo
```

- start demo:

```bash
bash scripts/demo_start.sh --env .env.demo
```

- backup rapido:

```bash
bash scripts/demo_backup.sh --env .env.demo --label pre-demo
```

- limpieza render jobs (dry-run):

```bash
cd apps/api
python scripts/render_jobs_cleanup.py --db-path data/render_jobs.db --keep-last 200 --older-than-days 14
```

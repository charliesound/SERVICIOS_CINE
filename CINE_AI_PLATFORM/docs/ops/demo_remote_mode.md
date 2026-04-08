# Modo demo remoto (operacion)

## Objetivo
Ejecutar demo remota segura usando servidor en casa (Windows + WSL) y laptop remota conectada por hotspot del movil.

## Precondiciones
- Stack arriba con `deploy/docker-compose.wsl.yml`.
- ComfyUI disponible en host local o red privada del servidor.
- Acceso remoto configurado con Tailscale (recomendado) o Cloudflare Tunnel.

## Auth minima recomendada para demo
- Tailscale: control por identidad tailnet + ACL.
- Cloudflare Tunnel: Cloudflare Access habilitado (OTP o IdP).
- Referencia: `docs/security/demo_auth_minimal.md`.
- Auth basica reversible en nginx (opcional): `docs/security/demo_proxy_basic_auth.md`.

## Archivo de entorno recomendado para demo
- Plantilla: `deploy/.env.demo.example`
- Crear archivo operativo:

```bash
cp deploy/.env.demo.example .env.demo
```

- Ajustar valores:
  - `CORS_ORIGINS` con origen real de demo (tailnet o dominio tunnel).
  - `ENABLE_LEGACY_ROUTES=false`
  - `COMFYUI_BASE_URL` endpoint privado valido.

## Arranque en modo demo

```bash
docker compose --env-file .env.demo -f deploy/docker-compose.wsl.yml up -d --build
```

Tiempo esperable:
- arranque con imagen cacheada: 20-60 s
- arranque con rebuild completo: 2-5 min

## Smoke flow manual de demo
Suponiendo `DEMO_URL` (por ejemplo `https://cine-demo.tudominio.com` o `http://host.tailnet:8080`):

Referencia compacta: `docs/ops/demo_smoke_flow.md`
Render smoke minimo: `docs/ops/demo_render_smoke.md`

1) UI principal:

```bash
curl -I "$DEMO_URL/"
```

2) Health:

```bash
curl -s "$DEMO_URL/api/health"
```

3) Health details (incluye ComfyUI opcional):

```bash
curl -s "$DEMO_URL/api/health/details"
```

4) Verificar familia oficial storage:

```bash
curl -s "$DEMO_URL/api/storage/summary"
```

5) Estado operativo resumido:

```bash
curl -s "$DEMO_URL/api/ops/status"
```

6) Verificar frontera legacy segun entorno:
- con `ENABLE_LEGACY_ROUTES=false`, `/projects` debe devolver `404`.

Tiempo esperable smoke completo: 30-90 s.

## Checklist previa a demo
- [ ] `docker compose ... ps` muestra `api` y `web` en estado `Up`
- [ ] URL remota carga frontend
- [ ] `/api/health` responde `ok: true`
- [ ] `/api/health/details` responde y muestra estado ComfyUI
- [ ] `CORS_ORIGINS` coincide con origen real remoto
- [ ] `ENABLE_LEGACY_ROUTES=false` para demo
- [ ] Backup reciente de `apps/api/data`
- [ ] Logs de `api` y `web` limpios antes de iniciar la demo

## Recuperacion rapida si ComfyUI falla
Objetivo: mantener demo viva aunque render este degradado.

1. Confirmar degradacion:

```bash
curl -s "$DEMO_URL/api/health/details"
```

2. Verificar `health.integrations.comfyui.reachable=false`.
3. Confirmar `api/ops/status` sigue `ok=true`.
4. Continuar demo en modo editor/storage (sin ejecutar render dependiente).
5. Revisar logs API:

```bash
docker compose --env-file .env.demo -f deploy/docker-compose.wsl.yml logs -f api
```

6. Si se recupera ComfyUI, validar nuevamente `health/details` y retomar flujo completo.

## Recuperacion rapida si falla acceso remoto
- Tailscale:
  1. comprobar estado tailnet en servidor y laptop
  2. probar acceso local `http://localhost:8080`
  3. reiniciar cliente Tailscale en ambos extremos
- Cloudflare Tunnel:
  1. revisar estado `cloudflared`
  2. validar dominio/tunnel en panel
  3. probar acceso local `http://localhost:8080`

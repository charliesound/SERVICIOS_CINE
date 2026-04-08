# Demo preflight checklist

## Objetivo
Confirmar en 5-10 minutos que el stack esta listo antes de salir de casa.

## 0) Preparacion de entorno (1 min)
- [ ] `cp deploy/.env.demo.example .env.demo` (si no existe)
- [ ] `CORS_ORIGINS` ajustado al origen real de demo (tailnet o dominio tunnel)
- [ ] `ENABLE_LEGACY_ROUTES=false`
- [ ] `COMFYUI_BASE_URL` apunta a endpoint privado valido

## 1) Validacion Docker/Compose (30-60 s)

```bash
docker compose --env-file .env.demo -f deploy/docker-compose.wsl.yml config >/dev/null
docker compose --env-file .env.demo -f deploy/docker-compose.wsl.yml ps
```

- [ ] compose valido
- [ ] Docker Engine activo

## 2) Preflight tecnico (1-2 min)

```bash
bash scripts/demo_preflight.sh --env .env.demo
```

- [ ] sin fallos (`Preflight OK`)
- [ ] warnings aceptados/documentados

## 3) Arranque de stack demo (2-4 min)

```bash
bash scripts/demo_start.sh --env .env.demo
```

Con auth basica en proxy (opcional):

```bash
bash scripts/demo_start.sh --env .env.demo --with-basic-auth
```

- [ ] `api` y `web` en `Up` (`docker compose ... ps`)

## 4) Smoke manual (1-2 min)
Definir `DEMO_URL` (tailnet o tunnel):

```bash
export DEMO_URL="http://localhost:8080"
```

```bash
curl -I "$DEMO_URL/"
curl -s "$DEMO_URL/api/health"
curl -s "$DEMO_URL/api/ops/status"
curl -s "$DEMO_URL/api/storage/summary"
```

- [ ] UI responde 200
- [ ] health responde `ok: true`
- [ ] ops/status responde y muestra estado operativo
- [ ] storage/summary responde

## 5) Confirmacion ComfyUI opcional (30-60 s)

```bash
curl -s "$DEMO_URL/api/health/details"
```

- [ ] `health.integrations.comfyui.configured=true`
- [ ] si `reachable=false`, preparar fallback sin render (demo editor/storage)

## 6) Backup previo (1 min)

```bash
bash scripts/demo_backup.sh --env .env.demo --label pre-demo
```

- [ ] backup generado en `backups/`

## 7) Validacion acceso remoto (1-2 min)
- [ ] Tailscale: laptop remota alcanza `DEMO_URL`
- [ ] Cloudflare: dominio demo responde y Access aplicado (si se usa esta opcion)

## 8) Ultima verificacion antes de salir
- [ ] acceso remoto validado (Tailscale o Cloudflare Access)
- [ ] laptop/movil cargados
- [ ] plan B sin ComfyUI listo (datos/edicion)
- [ ] proyecto/escena/plano de ejemplo cargados para demo rapida
- [ ] assets de apoyo listos (capturas, prompts, guion breve)

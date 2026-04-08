# Demo failure recovery

## Prioridad operativa en vivo
1. Recuperar acceso UI (`/`).
2. Recuperar `api/health`.
3. Mantener flujo demo storage/editor aunque ComfyUI falle.

## Comandos base

```bash
docker compose --env-file .env.demo -f deploy/docker-compose.wsl.yml ps
bash scripts/demo_logs.sh --env .env.demo
```

## Matriz de diagnostico rapido

| Sintoma | Diagnostico inmediato | Accion concreta |
|---|---|---|
| Frontend no carga | `curl -I http://localhost:8080/` | `docker compose ... restart web` y revisar `bash scripts/demo_logs.sh --env .env.demo web` |
| Frontend carga pero API no responde | `curl -s http://localhost:8080/api/health` | `docker compose ... restart api` y revisar `bash scripts/demo_logs.sh --env .env.demo api` |
| `/api/health` falla | `docker compose ... ps` + logs api | si `api` no arranca: `docker compose ... up -d --build` |
| `/api/health/details` muestra `comfyui.reachable=false` | `curl -s http://localhost:8080/api/health/details` | continuar demo sin render (fallback storage/editor), no bloquear demo |
| Tailscale o acceso remoto no conecta | probar local `http://localhost:8080` | si local OK: corregir capa remota (Tailscale/Cloudflare), no tocar stack |
| CORS bloquea peticiones | revisar `CORS_ORIGINS` en `.env.demo` | actualizar origen exacto y aplicar `docker compose ... up -d --build` |
| Contenedor no arranca | `docker compose ... ps` muestra `Exit` | logs servicio y recrear stack `docker compose ... up -d --build` |

## Pasos detallados por caso

### 1) Frontend no carga
```bash
docker compose --env-file .env.demo -f deploy/docker-compose.wsl.yml restart web
bash scripts/demo_logs.sh --env .env.demo web
```

### 2) Frontend carga pero API no responde
```bash
docker compose --env-file .env.demo -f deploy/docker-compose.wsl.yml restart api
bash scripts/demo_logs.sh --env .env.demo api
curl -s http://localhost:8080/api/health
```

### 3) `/api/health` sigue fallando
```bash
docker compose --env-file .env.demo -f deploy/docker-compose.wsl.yml up -d --build
curl -s http://localhost:8080/api/health
```

### 4) ComfyUI no reachable (modo degradado)
```bash
curl -s http://localhost:8080/api/ops/status
curl -s http://localhost:8080/api/health/details
```
Decision en vivo:
- seguir demo con proyecto/escena/plano, edicion y storage
- omitir ejecuciones dependientes de render hasta recuperar ComfyUI

### 5) Acceso remoto caido
- Tailscale: validar estado en servidor/cliente, reiniciar cliente Tailscale.
- Cloudflare: validar `cloudflared`, DNS/tunnel y policy de Access.
- Si local funciona, problema es de capa remota, no del stack.

### 6) CORS bloqueado
1. editar `.env.demo`
2. fijar `CORS_ORIGINS` al origen real remoto
3. reaplicar:

```bash
docker compose --env-file .env.demo -f deploy/docker-compose.wsl.yml up -d --build
```

## Fallback oficial sin ComfyUI
- Estado esperado: API y frontend vivos, ComfyUI degradado.
- Flujo de demo recomendado:
  1. abrir proyecto
  2. navegar escenas y shots
  3. editar metadata/prompts
  4. exportar/importar storage si aplica

## Recuperacion de datos (ultimo recurso)
- Restaurar segun `docs/ops/backup_restore.md`.

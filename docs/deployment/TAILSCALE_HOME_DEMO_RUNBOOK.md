# Tailscale Home Demo Runbook

## 1. Arquitectura

Movil / portatil
-> Tailscale
-> PC casa
-> Docker CID
-> ComfyUI local

## 2. Requisitos

- Tailscale activo en el PC
- Tailscale activo en movil y portatil
- Docker Desktop
- WSL Ubuntu
- Repo en `/opt/SERVICIOS_CINE`
- ComfyUI opcional para storyboard IA

## 3. Arranque

### Desde Windows

`arranque_ailinkcinema_cid_demo.bat`

### Desde WSL

`./scripts/start_home_demo.sh`

## 4. URLs

- `http://100.121.83.126`
- `http://100.121.83.126:3000`
- `http://100.121.83.126:8000`
- `http://100.121.83.126:8188`

## 5. Comprobacion

`./scripts/check_home_demo_health.sh`

## 6. Parada

`./scripts/stop_home_demo.sh`

## 7. Troubleshooting

- `.env` no existe: copiar desde `.env.home.example` o restaurar el `.env` real antes de arrancar.
- Conexion reset: revisar `docker compose ... ps` y confirmar que `frontend`, `backend` y `reverse-proxy` estan levantados.
- Contenedor en `restarting`: revisar logs del servicio afectado.
- Puerto ocupado: comprobar puertos `80`, `3000` y `8000` en Windows y WSL.
- Movil no conectado a Tailscale: abrir la app y verificar que ve la tailnet.
- Firewall de Windows: aplicar reglas para trafico Tailscale en `80`, `3000`, `8000` y `8188`.
- ComfyUI no escucha con `--listen 0.0.0.0`: solo se vera localmente; para pruebas remotas hay que revisar el bind del host.
- Si ComfyUI corre en WSL pero no responde en la IP Tailscale del PC, crear `portproxy` de Windows desde `100.121.83.126:8188` hacia `172.24.174.31:8188` y mantener la regla de firewall Tailscale.
- Vite / backend escuchan solo localhost: en este setup Docker publica `80`, `3000` y `8000` en todas las interfaces del host.

## 8. Seguridad

- No abrir puertos en el router.
- No exponer ComfyUI publicamente.
- Rotar secretos antes de mover este setup a VPS o produccion.

## 9. Notas de operacion

- El arranque local usa `compose.base.yml + compose.home.yml + .env`.
- No depende de `docker-compose.local.yml` ni de `.env.local`.
- Para acceso desde el frontend en `:3000`, la build queda apuntando a `/api` para evitar problemas de CORS en demo local.

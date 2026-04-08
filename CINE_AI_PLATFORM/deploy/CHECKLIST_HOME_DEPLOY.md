# CHECKLIST HOME DEPLOY

## Antes de ejecutar nada
- [ ] El disco externo esta conectado y visible con la letra esperada (`X:`).
- [ ] El repo abre correctamente desde el disco externo.
- [ ] Existe `.env.private` en la raiz del repo.
- [ ] `PRIVATE_BASE_URL` apunta al hostname real de Tailscale del ordenador de casa.
- [ ] `COMFYUI_BASE_URL=http://host.docker.internal:8188`.
- [ ] `COMFYUI_HOST_PROBE_URL=http://127.0.0.1:8188/system_stats`.
- [ ] Docker Desktop esta arrancado.
- [ ] WSL2 esta disponible.
- [ ] ComfyUI existe en la distro/ruta que se va a usar.
- [ ] Tailscale esta conectado.

## Secuencia obligatoria
- [ ] Arrancar ComfyUI en WSL2 con `deploy/start-comfy-wsl.ps1`.
- [ ] Verificar host -> ComfyUI con `infra/scripts/check-comfy-bridge.ps1 -SkipContainerCheck`.
- [ ] Levantar stack privado con `deploy/start-private.ps1`.
- [ ] Verificar host + contenedor con `infra/scripts/check-comfy-bridge.ps1`.
- [ ] Ejecutar smoke real con `infra/scripts/smoke-private.ps1`.

## Criterio de aceptacion
- [ ] `check-comfy-bridge.ps1 -SkipContainerCheck` devuelve `host_probe.ok = True`.
- [ ] `check-comfy-bridge.ps1` devuelve `host_probe.ok = True`.
- [ ] `check-comfy-bridge.ps1` devuelve `container_probe.ok = True`.
- [ ] `smoke-private.ps1` devuelve `api_health_ok = True`.
- [ ] `smoke-private.ps1` devuelve `api_health_details_ok = True`.
- [ ] `smoke-private.ps1` devuelve `comfyui_host_probe_ok = True`.
- [ ] `smoke-private.ps1` devuelve `comfyui_container_probe_ok = True`.

## Si algo falla
- [ ] Revisar `.env.private`.
- [ ] Revisar que ComfyUI este escuchando en `0.0.0.0:8188` dentro de WSL2.
- [ ] Revisar que Docker Desktop este arriba antes del `start-private.ps1`.
- [ ] Revisar que el hostname de Tailscale resuelva desde el host final.
- [ ] Revisar `docker compose ... ps` y logs si el stack no levanta completo.

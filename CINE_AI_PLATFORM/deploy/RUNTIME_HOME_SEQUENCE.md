# RUNTIME HOME SEQUENCE

## Fase 1: preparar host final

Comando:

```powershell
Get-Location
Test-Path .\.env.private
```

Salida esperada:
- el directorio actual es la raiz del repo
- `True` para `.env.private`

Si falla:
- abrir PowerShell en la raiz real del repo del disco externo
- crear o copiar `.env.private` desde `.env.private.example`

## Fase 2: arrancar ComfyUI en WSL2

Comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\start-comfy-wsl.ps1 -ComfyPath "/home/<user>/ComfyUI"
```

Salida esperada:
- salida con objeto que incluya `comfyui_base_url`
- `host_probe.ok = True`
- `container_probe.error = skipped`

Si falla:
- revisar que la ruta `-ComfyPath` exista en la distro correcta
- revisar que WSL2 este operativo
- revisar que ComfyUI arranque con `python main.py --listen 0.0.0.0 --port 8188`
- revisar que el puerto `8188` no este ocupado

## Fase 3: validar host Windows -> ComfyUI

Comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\check-comfy-bridge.ps1 -SkipContainerCheck
```

Salida esperada:
- `host_probe.ok = True`
- `host_probe.url = http://127.0.0.1:8188/system_stats`

Si falla:
- revisar que ComfyUI siga corriendo en WSL2
- revisar binding `0.0.0.0`
- revisar firewall local o conflictos de puerto

## Fase 4: levantar stack privado

Comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\start-private.ps1
```

Salida esperada:
- `docker compose ... ps` muestra `cine-private-api`, `cine-private-web`, `cine-private-nginx`, `cine-private-n8n`, `cine-private-qdrant`
- el script puede emitir warning si el bridge no esta listo; si ocurre, no continuar hasta revisarlo

Si falla:
- revisar que Docker Desktop este arriba
- revisar `.env.private`
- revisar disponibilidad de rutas `X:\CINE_AI_PLATFORM\storage\...`
- revisar `docker compose --env-file .env.private -f docker-compose.private.yml ps`

## Fase 5: validar host + contenedor -> ComfyUI

Comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\check-comfy-bridge.ps1
```

Salida esperada:
- `host_probe.ok = True`
- `container_probe.ok = True`
- `container_probe.url = http://host.docker.internal:8188/system_stats`

Si falla:
- si falla `host_probe`, volver a Fase 2
- si falla `container_probe`, revisar que el servicio `api` este `Up`
- revisar `COMFYUI_BASE_URL` en `.env.private`
- revisar conectividad Docker Desktop -> `host.docker.internal`

## Fase 6: smoke real por Tailscale

Comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\smoke-private.ps1
```

Salida esperada:
- `api_health_ok = True`
- `api_health_details_ok = True`
- `comfyui_health_reachable = True`
- `comfyui_host_probe_ok = True`
- `comfyui_container_probe_ok = True`

Si falla:
- revisar `PRIVATE_BASE_URL` en `.env.private`
- revisar Tailscale en el host final
- revisar que nginx este arriba
- revisar que el login demo siga configurado en `AUTH_BOOTSTRAP_USERS`

## Fase 7: parada controlada

Comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\stop-private.ps1
```

Salida esperada:
- compose detiene los servicios sin error

Si falla:
- ejecutar `docker compose --env-file .env.private -f docker-compose.private.yml ps`
- revisar si quedan contenedores en reinicio o bloqueo de Docker Desktop

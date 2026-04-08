# FIRST BOOT PRIVATE

## Antes del primer arranque en el ordenador de casa
- comprobar que existe `.env.private`
- cambiar `N8N_ENCRYPTION_KEY`
- cambiar la password de `AUTH_BOOTSTRAP_USERS`
- revisar `PRIVATE_BASE_URL` con el hostname real de Tailscale
- revisar `PRIVATE_BROWSER_ORIGINS`
- revisar `N8N_HOST`
- revisar `N8N_EDITOR_BASE_URL`
- revisar `N8N_WEBHOOK_URL`
- confirmar `COMFYUI_BASE_URL=http://host.docker.internal:8188`
- confirmar `COMFYUI_HOST_PROBE_URL=http://127.0.0.1:8188/system_stats`
- confirmar rutas del disco externo:
  - `API_DATA_PATH`
  - `N8N_DATA_PATH`
  - `QDRANT_STORAGE_PATH`
  - `NGINX_LOG_PATH`
- no continuar si quedan placeholders `CHANGE_ME_*`

## Orden minimo del primer arranque
1. Abrir PowerShell en la raiz del repo del disco externo.
2. Arrancar ComfyUI en WSL2:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\start-comfy-wsl.ps1 -ComfyPath "/home/<user>/ComfyUI"
```

3. Verificar host Windows -> ComfyUI:

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\check-comfy-bridge.ps1 -SkipContainerCheck
```

4. Levantar stack privado:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\start-private.ps1
```

5. Verificar host + contenedor -> ComfyUI:

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\check-comfy-bridge.ps1
```

6. Ejecutar smoke real con la password real del admin:

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\smoke-private.ps1 -AdminPassword "<admin-password-real>"
```

## Revisiones previas al stack
- Docker Desktop disponible
- WSL2 disponible
- Tailscale conectado
- ComfyUI accesible en la distro/ruta elegida
- disco externo montado con la ruta esperada

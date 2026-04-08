# ComfyUI Bridge Private

Documento de predeploy para preparar el bridge antes de mover el disco al ordenador de casa.

## Valor fijo del bridge
- `COMFYUI_BASE_URL=http://host.docker.internal:8188`
- `COMFYUI_HOST_PROBE_URL=http://127.0.0.1:8188/system_stats`

## Estado actual
- El bridge queda preparado, no validado todavia en runtime real.
- La validacion real solo se ejecuta en el ordenador de casa, donde existan Docker Desktop, WSL2, ComfyUI y Tailscale.

## Scripts por fase

### En laptop durante preparacion
```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\predeploy-validate.ps1
```

Valida:
- presencia de archivos
- parseo PowerShell
- `docker compose config` con `.env.private.example`

No valida:
- ComfyUI real
- WSL2 real
- bridge host/container
- Tailscale real

### En el ordenador de casa durante despliegue real
1. Arrancar ComfyUI en WSL2:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\start-comfy-wsl.ps1 -ComfyPath "/home/<user>/ComfyUI"
```

Comando esperado en WSL2:

```bash
python main.py --listen 0.0.0.0 --port 8188
```

2. Verificar solo host Windows -> ComfyUI:

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\check-comfy-bridge.ps1 -SkipContainerCheck
```

3. Levantar el stack privado:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\start-private.ps1
```

4. Verificar Windows host -> ComfyUI y contenedor `api` -> `COMFYUI_BASE_URL`:

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\check-comfy-bridge.ps1
```

Esperado en el host final:
- `host_probe.ok = True`
- `container_probe.ok = True`

5. Ejecutar smoke privado real:

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\smoke-private.ps1
```

`smoke-private.ps1` usa `PRIVATE_BASE_URL` por defecto y falla si el bridge a ComfyUI no responde desde Windows host o desde el contenedor `api`.

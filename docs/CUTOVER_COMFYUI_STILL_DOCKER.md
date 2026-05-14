# Cutover ComfyUI Still Native 8188 → Docker 8188

## 1) Objetivo

- Sustituir la instancia ComfyUI still nativa en puerto `8188` por Docker still en `8188`.
- Mantener el mismo source of truth de modelos: `/mnt/i/COMFYUI_OK/models`
- Mantener el mismo hub operativo: `/mnt/g/COMFYUI_HUB`
- No interrumpir las instancias nativas de video/dubbing/restoration/3d (8189–8192).

## 2) Estado actual validado

- ComfyUI still nativo en `8188` activo (validado en Infra 8A y operativo continuo).
- Docker still validado en `8288` (Infra 8E).
- Generacion directa `/prompt` contra Docker still 8288 exitosa (Infra 8G).
- Generacion via infraestructura CID contra Docker still 8288 exitosa (Infra 8H).
- Misma ruta de modelos y hub usada por Docker still en modo validacion.

## 3) Preflight obligatorio

Antes de iniciar el cutover, ejecutar:

```bash
cd /opt/SERVICIOS_CINE

git status --short
# Esperado: solo ?? AGENTS.md

curl -sf http://127.0.0.1:8188/system_stats >/dev/null && echo "nativo still 8188 OK"
curl -sf http://127.0.0.1:8288/system_stats >/dev/null && echo "docker still 8288 OK"

docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep -i comfy || true

nvidia-smi

ls -ld /mnt/i/COMFYUI_OK/models
ls -ld /mnt/g/COMFYUI_HUB/output/still
ls /mnt/i/COMFYUI_OK/models/checkpoints/realisticVisionV60B1_v51VAE.safetensors
```

## 4) Estrategia de cutover

### Paso A — Detener ComfyUI still nativo

```bash
# Identificar proceso nativo still en 8188
PID_STILL=$(ss -ltnp | awk '/:8188/ {print $NF}' | sed -n 's/.*pid=\([0-9]\+\).*/\1/p')
kill "$PID_STILL"
sleep 5
ss -ltnp | grep ':8188' || echo "8188 libre"
```

No tocar procesos en 8189–8192.

### Paso B — Arrancar Docker still en 8188

```bash
# Opcion preferida: compose con puerto 8188
COMFYUI_IMAGE=yanwk/comfyui-boot:cu130-slim-v2 \
COMFYUI_STILL_HOST_PORT=8188 \
COMFYUI_CONTAINER_ROOT=/root/ComfyUI \
COMFYUI_MODELS_BASE_DIR=/mnt/i/COMFYUI_OK/models \
COMFYUI_HUB_DIR=/mnt/g/COMFYUI_HUB \
docker compose -f compose.base.yml -f compose.comfyui.yml -f compose.comfyui.gpu.yml \
  --profile with-comfyui up -d comfyui-still
```

### Paso C — Validar Docker still en 8188

```bash
curl -sf http://127.0.0.1:8188/system_stats >/dev/null && echo "HTTP 200"
curl -sf http://127.0.0.1:8188/api/object_info >/dev/null && echo "object_info OK"
docker exec servicios_cine-comfyui-still-1 nvidia-smi | grep "RTX 5090"
find /mnt/g/COMFYUI_HUB/output/still -writable | head -3
```

### Paso D — Reconfigurar backend CID

En el entorno de ejecucion del backend:

```bash
COMFYUI_STILL_BASE_URL=http://127.0.0.1:8188
```

O, si es el default nativo, simplemente no sobreescribir.

### Paso E — Smoke CID

```bash
# Health
curl http://127.0.0.1:8000/api/v1/comfyui/health

# Instances
curl http://127.0.0.1:8000/api/v1/comfyui/instances

# Resolve still
curl http://127.0.0.1:8000/api/v1/comfyui/resolve/still

# Resolve storyboard
curl http://127.0.0.1:8000/api/v1/comfyui/resolve/storyboard_realistic

# Capabilities
curl http://127.0.0.1:8000/api/ops/capabilities

# Generacion minima desde CID (opcional)
```

## 5) Rollback

```bash
# 1. Detener Docker still
docker rm -f servicios_cine-comfyui-still-1

# 2. Arrancar nativo still
cd ~/ai/ComfyUI_instances/ComfyUI-image
python main.py --listen 0.0.0.0 --port 8188 &
sleep 15

# 3. Confirmar
curl -sf http://127.0.0.1:8188/system_stats >/dev/null && echo "nativo 8188 restaurado"
```

No tocar modelos, outputs ni volumenes durante rollback.

## 6) Criterios GO

- Docker still 8188 responde `HTTP 200` en `/system_stats`.
- `GET /api/object_info` responde `HTTP 200`.
- CID resuelve `still` y `storyboard_realistic` contra `127.0.0.1:8188`.
- Generacion minima exitosa desde CID.
- Sin OOM ni errores en Docker logs.
- Instancias nativas en 8189–8192 intactas.

## 7) Criterios NO-GO

- Docker no arranca en puerto 8188.
- `/object_info` falla.
- Output no se escribe en `/mnt/g/COMFYUI_HUB/output/still`.
- CID sigue apuntando al contenedor de validacion 8288 o a direccion incorrecta.
- OOM detectado.
- Perdida de acceso a modelos montados.
- Errores de permisos en `/mnt/g/COMFYUI_HUB`.

## 8) Notas de seguridad

- No exponer ComfyUI Docker directamente al usuario; el routing debe pasar por CID.
- Tailscale/Caddy solo deben exponer CID, no ComfyUI directamente.
- No ejecutar este cutover si algun smoke de validacion 8G/8H ha fallado.
- No ejecutar mientras haya jobs CID activos contra still nativo.

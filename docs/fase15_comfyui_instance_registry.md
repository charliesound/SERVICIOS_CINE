# Fase 1.5 — ComfyUI Instance Registry CID

## Objetivo

Implementar un registry central de instancias ComfyUI que permita a CID
resolver qué instancia debe ejecutar un workflow según el `task_type`,
sin hardcodear puertos ni URLs en el código de negocio.

## Arquitectura

```
┌──────────────────────────────────────────────────┐
│                   CID (FastAPI)                    │
│                                                    │
│  /api/v1/comfyui/...  ──►  comfyui_instance_routes │
│                                   │                │
│                                   ▼                │
│                     comfyui_instance_registry      │
│                                   │                │
│                                   ▼                │
│                   ┌─── YAML (config) ───┐          │
│                   │  comfyui_instances   │          │
│                   │  .yml                │          │
│                   └──────────────────────┘          │
│                                   │                │
│                         env overrides               │
│                   COMFYUI_*_URL env vars            │
│                                                    │
│                   ┌─── HTTP ───┐                   │
│                   │  httpx.     │                   │
│                   │  AsyncClient│                   │
│                   └────────────┘                   │
│                         │                          │
└─────────────────────────┼──────────────────────────┘
                          │
               ┌──────────┼──────────┬──────────┐
               ▼          ▼          ▼          ▼
         ComfyUI     ComfyUI    ComfyUI    ComfyUI
         :8188       :8189      :8190      :8191  :8192
         Image     Video/Cine  Dubbing   Restor.   3D
```

## Instancias registradas

| Clave | Nombre | Puerto | Task Types |
|-------|--------|--------|------------|
| `image` | Image | 8188 | image, storyboard, still |
| `video_cine` | Video/Cine | 8189 | video, cine, previz, i2v, t2v |
| `dubbing_audio` | DubbingAudio | 8190 | dubbing, audio, lipsync, voice |
| `restoration` | Restoration | 8191 | restoration, upscale, cleanup, repair |
| `three_d` | 3D | 8192 | 3d, depth, mesh, scene |

## Rutas API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/comfyui/instances` | Listar todas las instancias |
| GET | `/api/v1/comfyui/instances/{key}` | Obtener detalle de una instancia |
| GET | `/api/v1/comfyui/instances/{key}/health` | Health check de una instancia |
| GET | `/api/v1/comfyui/health` | Resumen de salud de todas las instancias |
| GET | `/api/v1/comfyui/resolve/{task_type}` | Resolver qué instancia ejecuta un task_type |

## Resolución task_type → instancia

| task_type | instancia | puerto |
|-----------|-----------|--------|
| `storyboard` | image | 8188 |
| `still` | image | 8188 |
| `image` | image | 8188 |
| `video` | video_cine | 8189 |
| `cine` | video_cine | 8189 |
| `previz` | video_cine | 8189 |
| `i2v` | video_cine | 8189 |
| `t2v` | video_cine | 8189 |
| `dubbing` | dubbing_audio | 8190 |
| `audio` | dubbing_audio | 8190 |
| `lipsync` | dubbing_audio | 8190 |
| `voice` | dubbing_audio | 8190 |
| `restoration` | restoration | 8191 |
| `upscale` | restoration | 8191 |
| `cleanup` | restoration | 8191 |
| `repair` | restoration | 8191 |
| `3d` | three_d | 8192 |
| `depth` | three_d | 8192 |
| `mesh` | three_d | 8192 |
| `scene` | three_d | 8192 |

## YAML

Archivo: `src/config/comfyui_instances.yml`

```yaml
instances:
  image:
    name: "Image"
    base_url: "http://127.0.0.1:8188"
    port: 8188
    enabled: true
    task_types: ["image", "storyboard", "still"]
    health_endpoint: "/system_stats"

  video_cine:
    name: "Video/Cine"
    base_url: "http://127.0.0.1:8189"
    port: 8189
    enabled: true
    task_types: ["video", "cine", "previz", "i2v", "t2v"]
    health_endpoint: "/system_stats"

  dubbing_audio:
    name: "DubbingAudio"
    base_url: "http://127.0.0.1:8190"
    port: 8190
    enabled: true
    task_types: ["dubbing", "audio", "lipsync", "voice"]
    health_endpoint: "/system_stats"

  restoration:
    name: "Restoration"
    base_url: "http://127.0.0.1:8191"
    port: 8191
    enabled: true
    task_types: ["restoration", "upscale", "cleanup", "repair"]
    health_endpoint: "/system_stats"

  three_d:
    name: "3D"
    base_url: "http://127.0.0.1:8192"
    port: 8192
    enabled: true
    task_types: ["3d", "depth", "mesh", "scene"]
    health_endpoint: "/system_stats"
```

## Env vars

```
COMFYUI_INSTANCES_CONFIG=src/config/comfyui_instances.yml
COMFYUI_IMAGE_URL=http://127.0.0.1:8188
COMFYUI_VIDEO_CINE_URL=http://127.0.0.1:8189
COMFYUI_DUBBING_AUDIO_URL=http://127.0.0.1:8190
COMFYUI_RESTORATION_URL=http://127.0.0.1:8191
COMFYUI_3D_URL=http://127.0.0.1:8192
COMFYUI_TIMEOUT_SECONDS=120
COMFYUI_HEALTH_TIMEOUT_SECONDS=5
COMFYUI_POLL_INTERVAL_SECONDS=2
```

Los `COMFYUI_*_URL` permiten sobrescribir la URL de cada instancia
desde entorno (útil para entornos con Tailscale, Docker, etc.).

## Cómo validar

```bash
# Compilar
python -m compileall src/

# Tests unitarios
python -m pytest tests/unit/test_comfyui_instance_registry.py -v
python -m pytest tests/unit/test_comfyui_instance_routes.py -v

# Tests completos
python -m pytest tests/unit/ -q
python -m pytest tests/integration/ -q

# Alembic heads
alembic heads

# Arrancar backend
PYTHONPATH=src uvicorn app:app --host 127.0.0.1 --port 8010

# Endpoints
curl -s http://127.0.0.1:8010/api/v1/comfyui/instances | jq .
curl -s http://127.0.0.1:8010/api/v1/comfyui/resolve/storyboard | jq .
curl -s http://127.0.0.1:8010/api/v1/comfyui/resolve/i2v | jq .
curl -s http://127.0.0.1:8010/api/v1/comfyui/resolve/lipsync | jq .
curl -s http://127.0.0.1:8010/api/v1/comfyui/resolve/upscale | jq .
curl -s http://127.0.0.1:8010/api/v1/comfyui/resolve/mesh | jq .
curl -s http://127.0.0.1:8010/api/v1/comfyui/health | jq .

# Health legacy
curl -i http://127.0.0.1:8010/health/live
curl -i http://127.0.0.1:8010/health/ready
curl -i http://127.0.0.1:8010/health/startup

# request_id
curl -i -H "X-Request-ID: cid-test-001" http://127.0.0.1:8010/ruta-inexistente
```

## Limitaciones

- No implementa ejecución de workflows (Fase 2)
- No implementa capabilities por instancia
- No implementa selección inteligente por carga
- No implementa fallback automático entre instancias
- Asume que cada instancia responde en `/system_stats`
- Sin cache de health checks (cada llamada hace HTTP real)

## Siguiente fase posible

1. **Ejecución de workflows**: POST a la instancia resuelta
2. **Capabilities por instancia**: qué modelos/flujos soporta cada una
3. **Selección inteligente por carga**: elegir la instancia menos cargada
4. **Fallback automático**: si una instancia falla, redirigir a otra compatible
5. **Cache de health**: evitar llamadas HTTP repetitivas

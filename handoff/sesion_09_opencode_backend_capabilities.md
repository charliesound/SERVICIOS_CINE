# SESION 09: OpenCode - Backend Capabilities

## Rol
Senior Backend Engineer

## Ruta de Trabajo
`D:\SERVICIOS_CINE\src`

## Objetivo
Implementar detector de capacidades reales de cada backend ComfyUI.

## Backends a Detectar
- still: 8188
- video: 8189
- dubbing: 8190
- lab: 8191

## Informacion a Recopilar
- Health status
- Modelos/checkpoints detectados
- Nodos disponibles
- Capacidades inferidas
- Tiempo de respuesta
- Warnings

## Archivos a Crear/Verificar

### 1. services/backend_capability_service.py (ya existe)
Verificar que incluye:
- NodeInfo dataclass
- ModelInfo dataclass
- BackendCapabilities dataclass
- BackendCapabilityService singleton
- detect_capabilities()
- detect_all_capabilities()
- can_workflow_run()

### 2. routes/ops_routes.py (ya existe)
Verificar endpoints:
- GET /api/ops/instances
- GET /api/ops/capabilities
- GET /api/ops/capabilities/{backend}
- GET /api/ops/status
- POST /api/ops/instances/{backend}/health-check
- GET /api/ops/can-run

## Capacidades Inferidas
- image_generation: si hay CheckpointLoader
- sampling: si hay KSampler
- video_output: si hay SaveAnimatedWEBP
- video_generation: si hay AnimateDiff
- audio_processing: si hay LoadAudio/SaveAudio/TTS
- voice_cloning: si hay VoiceClone
- inpainting: si hay nodos Inpaint
- upscaling: si hay nodos Upscale

## Integracion con Planner/Validator
```python
can_run, missing = capability_service.can_workflow_run(
    backend="still",
    required_capabilities=["image_generation", "sampling"]
)
```

## Smoke Test
```bash
# Status consolidado
curl http://localhost:8000/api/ops/status

# Capacidades de backend
curl http://localhost:8000/api/ops/capabilities/still

# Forzar refresh
curl "http://localhost:8000/api/ops/capabilities?force_refresh=true"

# Verificar si puede ejecutar
curl "http://localhost:8000/api/ops/can-run?backend=still&capabilities=image_generation,sampling"
```

## Response Example
```json
{
  "backends": {
    "still": {
      "backend": "still",
      "healthy": true,
      "response_time_ms": 45.23,
      "comfyui_version": "1.2.1",
      "nodes_count": 47,
      "models_count": 12,
      "detected_capabilities": ["image_generation", "sampling", "image_decoding"],
      "warnings": [],
      "last_check": "2026-04-06T12:30:00"
    }
  }
}
```

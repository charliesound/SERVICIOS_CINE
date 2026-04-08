# SERVICIOS_CINE Backend

Backend FastAPI principal de `SERVICIOS_CINE`.

## Arranque local

```bash
cd /opt/SERVICIOS_CINE/src
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API local:

- `http://localhost:8000`
- `http://localhost:8000/docs`

Para el despliegue actual con Docker y Caddy, usa `README_WSL2.md` y `DOCKER.md`.

## Estructura

```
src/
├── app.py                    # FastAPI application entry point
├── config/
│   ├── config.yaml          # Main configuration
│   ├── instances.yml        # Backend instances definition
│   ├── plans.yml            # User plans and limits
│   └── example_capabilities_response.json
├── services/
│   ├── instance_registry.py       # Backend instance management
│   ├── comfyui_client_factory.py  # Client factory for ComfyUI backends
│   ├── job_router.py              # Job routing logic
│   ├── queue_service.py           # Queue state management
│   ├── job_scheduler.py            # Job scheduler loop
│   ├── plan_limits_service.py      # Plan limits and tracking
│   ├── user_service.py            # User management
│   ├── workflow_registry.py        # Workflow templates registry
│   ├── workflow_planner.py         # Intent analysis and workflow selection
│   ├── workflow_builder.py         # JSON workflow construction
│   ├── workflow_validator.py       # Workflow validation
│   ├── workflow_preset_service.py  # User presets management
│   └── backend_capability_service.py # Backend capability detection
├── routes/
│   ├── auth_routes.py
│   ├── user_routes.py
│   ├── render_routes.py
│   ├── queue_routes.py
│   ├── workflow_routes.py
│   ├── plan_routes.py
│   ├── admin_routes.py
│   └── ops_routes.py
├── schemas/
│   └── (Pydantic models)
└── tests/
    └── smoke_ops.bat
```

## Puertos de backends externos

| Backend  | Port | Purpose              |
|----------|------|----------------------|
| still    | 8188 | Image generation     |
| video    | 8189 | Video generation     |
| dubbing  | 8190 | Voice/Audio          |
| lab      | 8191 | Experimental         |

## Endpoints clave

### Jobs
- `POST /api/render/jobs` - Submit a new job
- `GET /api/render/jobs/{job_id}` - Get job status
- `POST /api/render/jobs/{job_id}/retry` - Retry failed job

### Queue
- `GET /api/queue/status` - Get queue status
- `GET /api/queue/status/{job_id}` - Get specific job queue status

### Workflows
- `POST /api/workflows/plan` - Plan workflow from intent
- `POST /api/workflows/build` - Build workflow JSON
- `POST /api/workflows/validate` - Validate workflow
- `GET /api/workflows/catalog` - List available workflows
- `GET /api/workflows/presets` - List presets

### Plans
- `GET /api/plans/catalog` - List all plans
- `GET /api/plans/me` - Get current user plan limits

### Ops
- `GET /api/ops/instances` - Get backend instance status
- `GET /api/ops/capabilities` - Get backend capabilities
- `GET /api/ops/capabilities/{backend}` - Get specific backend capabilities
- `GET /api/ops/can-run` - Check if backend can run required capabilities

## Scheduler

El scheduler arranca automaticamente al iniciar la app:
- Poll interval: 5 seconds
- Job timeout: 3600 seconds (1 hour)
- Manages concurrency per backend

## Cola de prioridad

Los jobs se ordenan por:
1. Priority score (plan-based, higher is better)
2. Submission time (FIFO)

## Ejemplo de envio de job

```bash
curl -X POST "http://localhost:8000/api/render/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "still",
    "workflow_key": "still_text_to_image_pro",
    "prompt": {
      "positive": "cinematic shot of a robot in sunset",
      "negative": "blurry, low quality"
    },
    "user_id": "user123",
    "user_plan": "free",
    "priority": 5
  }'
```

## Artefactos locales

Los artefactos locales como `.env`, `.venv/`, `__pycache__/`, `logs/` y `data/` no forman parte del versionado operativo.

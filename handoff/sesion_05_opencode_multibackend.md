# SESION 05: OpenCode - Routing Multi-Backend

## Rol
Senior Backend Engineer

## Ruta de Trabajo
`D:\SERVICIOS_CINE\src`

## Objetivo
Implementar sistema de routing a backends ComfyUI:
- still -> 8188
- video -> 8189
- dubbing -> 8190
- lab -> 8191

## Archivos a Crear/Modificar

### 1. config/instances.yml (ya existe)
Verificar contenido:
```yaml
backends:
  still:
    port: 8188
    base_url: "http://localhost:8188"
  video:
    port: 8189
    base_url: "http://localhost:8189"
  dubbing:
    port: 8190
    base_url: "http://localhost:8190"
  lab:
    port: 8191
    base_url: "http://localhost:8191"
```

### 2. services/instance_registry.py (ya existe)
Verificar que incluye:
- BackendInstance dataclass
- InstanceRegistry singleton
- get_backend(), get_all_backends()
- resolve_backend_for_task()

### 3. services/comfyui_client_factory.py (ya existe)
Verificar que incluye:
- ComfyUIClient class
- ComfyUIFactory singleton
- get_client(), get_client_for_task()

### 4. services/job_router.py (ya existe)
Verificar que incluye:
- JobRequest/Job dataclass
- JobRouter singleton
- route_job() con logica de seleccion de backend

### 5. routes/render_routes.py (ya existe)
Verificar endpoints:
- POST /api/render/jobs
- GET /api/render/jobs/{job_id}
- GET /api/render/jobs

## Reglas de Routing
- task_type=still -> backend=still
- task_type=video -> backend=video
- task_type=dubbing -> backend=dubbing
- task_type=experimental -> backend=lab
- fallback -> still

## Smoke Test
```bash
curl -X POST http://localhost:8000/api/render/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "still",
    "workflow_key": "still_text_to_image_pro",
    "prompt": {"positive": "test"},
    "user_id": "test",
    "user_plan": "free"
  }'
```

## Validacion
Verificar que la respuesta incluye:
- job_id
- backend (debe ser "still")
- backend_url (debe incluir 8188)

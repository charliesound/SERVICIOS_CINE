# SESION 07: OpenCode - Planes y Limites

## Rol
Senior Backend Engineer

## Ruta de Trabajo
`D:\SERVICIOS_CINE\src`

## Objetivo
Implementar sistema de planes con limites por usuario.

## Planes a Implementar

| Plan | Jobs Activos | Jobs Cola | Priority | Servicios |
|------|--------------|-----------|----------|----------|
| free | 1 | 2 | 1 | still |
| creator | 2 | 5 | 2 | still, dubbing |
| studio | 3 | 10 | 3 | still, video, dubbing |
| enterprise | 5 | 20 | 4 | all |

## Archivos a Crear/Verificar

### 1. config/plans.yml (ya existe)
Verificar estructura:
```yaml
plans:
  free:
    max_active_jobs: 1
    max_queued_jobs: 2
    priority_score: 1
    allowed_task_types: ["still"]
  # ... resto de planes
```

### 2. services/plan_limits_service.py (ya existe)
Verificar que incluye:
- PlanLimits dataclass
- PlanLimitsService singleton
- UserPlanTracker singleton
- can_run_task()
- validate_job_submission()
- track_active_job(), track_queued_job()

### 3. routes/plan_routes.py (ya existe)
Verificar endpoints:
- GET /api/plans/catalog
- GET /api/plans/me?user_id=X&plan_name=Y
- GET /api/plans/{plan_name}
- GET /api/plans/{plan_name}/can-run/{task_type}

## Priorizacion de Cola
Jobs se ordenan por:
1. priority_score DESC (planes premium primero)
2. created_at ASC (FIFO)

## Validacion en Render
Antes de crear job, verificar:
1. Plan existe
2. Plan permite task_type
3. Usuario no supero limites de jobs

## Smoke Test
```bash
# Ver catalogo
curl http://localhost:8000/api/plans/catalog

# Ver si plan permite tarea
curl http://localhost:8000/api/plans/free/can-run/video

# Ver estado de plan de usuario
curl "http://localhost:8000/api/plans/me?user_id=u1&plan_name=free"
```

## Response Example
```json
{
  "plan": "free",
  "active_jobs": 0,
  "max_active_jobs": 1,
  "queued_jobs": 0,
  "max_queued_jobs": 2,
  "can_submit_active": true,
  "can_submit_queued": true,
  "priority_score": 1
}
```

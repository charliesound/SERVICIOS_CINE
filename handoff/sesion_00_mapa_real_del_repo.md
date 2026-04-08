# SESION 00: Mapa Real del Repositorio

## Estructura Actual

```
D:\SERVICIOS_CINE
├─ src                          # BACKEND CANDIDATO PRINCIPAL
├─ src_frontend                 # FRONTEND CANDIDATO PRINCIPAL  
├─ CID_SERVER                   # Proyecto heredado - Auditar
├─ CINE_AI_PLATFORM             # Proyecto heredado - Auditar
├─ PROYECTO FINAL V1            # Proyecto heredado - Auditar
├─ Web Ailink_Cinema            # Proyecto heredado - Auditar
└─ handoff                      # Documentación de handoff
```

## Descripción de Carpetas

### src (BACKEND)
Backend FastAPI principal con:
- routes/ (9 archivos: auth, user, render, queue, workflow, plan, admin, ops, demo)
- services/ (15 archivos: instance_registry, comfyui_client_factory, job_router, queue_service, job_scheduler, plan_limits_service, workflow_*, backend_capability_service, demo_service)
- schemas/ (6 archivos: auth, user, job, queue, workflow, plan)
- config/ (instances.yml, plans.yml, config.yaml)
- app.py, config.py, requirements.txt

### src_frontend (FRONTEND)
Frontend React+TypeScript+Vite con:
- api/ (6 servicios: auth, render, queue, workflow, plans, ops)
- components/ (6: Layout, BackendStatusPanel, QueueStatusPanel, WorkflowPlannerPanel, JobSubmitForm, PlanBadge)
- pages/ (7: Dashboard, CreateJob, QueuePage, WorkflowsPage, PlansPage, AdminPage, LoginPage)
- hooks/ (5: useBackend, useJobs, useWorkflow, useQueue, usePlans)
- store/ (Zustand: authStore, jobStore)
- types/, utils/

### CID_SERVER
Proyecto heredado a auditar.

### CINE_AI_PLATFORM
Proyecto heredado a auditar.

### PROYECTO FINAL V1
Proyecto heredado a auditar.

### Web Ailink_Cinema
Frontend heredado a auditar.

## Roles Asignados

| Carpeta | Rol | Estado |
|---------|-----|--------|
| src | Backend candidato | En desarrollo |
| src_frontend | Frontend candidato | En desarrollo |
| CID_SERVER | Fuente/Integración | Por auditar |
| CINE_AI_PLATFORM | Fuente/Integración | Por auditar |
| PROYECTO FINAL V1 | Fuente/Integración | Por auditar |
| Web Ailink_Cinema | Fuente/Integración | Por auditar |

## Backends ComfyUI Configurados

| Backend | Puerto | Propósito |
|---------|--------|----------|
| still | 8188 | Generación de imágenes |
| video | 8189 | Generación de video |
| dubbing | 8190 | Voz y audio |
| lab | 8191 | Experimental |

## Planes Configurados

| Plan | Jobs Activos | Jobs Cola | Servicios |
|------|--------------|-----------|----------|
| free | 1 | 2 | still |
| creator | 2 | 5 | still, dubbing |
| studio | 3 | 10 | still, video, dubbing |
| enterprise | 5 | 20 | still, video, dubbing, experimental |

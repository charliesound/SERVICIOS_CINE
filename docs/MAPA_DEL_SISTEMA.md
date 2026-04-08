# Mapa del Sistema SERVICIOS_CINE

## Diagrama de Arquitectura

```
                            ┌─────────────────────┐
                            │     USUARIO         │
                            └──────────┬──────────┘
                                       │
                            ┌──────────▼──────────┐
                            │   FRONTEND (3000)   │
                            │   React + TypeScript │
                            │   src_frontend/     │
                            └──────────┬──────────┘
                                       │ HTTP
                            ┌──────────▼──────────┐
                            │   BACKEND (8000)    │
                            │   FastAPI + Python   │
                            │      src/           │
                            └──────────┬──────────┘
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          │                            │                            │
┌─────────▼─────────┐     ┌────────────▼────────┐     ┌────────────▼────────┐
│  PLANES Y LIMITES │     │  QUEUE + SCHEDULER │     │  WORKFLOW ENGINE    │
│  - free           │     │  - Concurrencia    │     │  - Registry         │
│  - creator        │     │  - Prioridad       │     │  - Planner          │
│  - studio         │     │  - Estados         │     │  - Builder          │
│  - enterprise     │     │  - Timeout         │     │  - Validator        │
└───────────────────┘     └────────────┬────────┘     └────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
          ┌─────────▼────┐   ┌────────▼────┐   ┌───────▼───────┐
          │   STILL     │   │   VIDEO     │   │   DUBBING     │
          │   :8188    │   │   :8189     │   │   :8190       │
          │  ComfyUI   │   │  ComfyUI   │   │  ComfyUI      │
          └─────────────┘   └─────────────┘   └───────────────┘
                                      │
                            ┌──────────▼──────────┐
                            │   LAB (8191)        │
                            │   Experimental      │
                            └─────────────────────┘
```

## Modulos Principales

### Nucleo del Backend (src/)

```
src/
├── app.py                          # FastAPI entry point
├── config.py                       # Config loader
│
├── config/                         # Configuracion YAML
│   ├── config.yaml                # App settings
│   ├── instances.yml               # Backends (8188-8191)
│   └── plans.yml                  # Planes y limites
│
├── routes/                         # ENDPOINTS API
│   ├── auth_routes.py            # /api/auth/*
│   ├── user_routes.py            # /api/users/*
│   ├── render_routes.py          # /api/render/jobs
│   ├── queue_routes.py           # /api/queue/*
│   ├── workflow_routes.py         # /api/workflows/*
│   ├── plan_routes.py            # /api/plans/*
│   ├── ops_routes.py             # /api/ops/*
│   ├── admin_routes.py           # /api/admin/*
│   └── demo_routes.py            # /api/demo/*
│
├── services/                       # LOGICA DE NEGOCIO
│   ├── instance_registry.py      # Gestion de backends
│   ├── comfyui_client_factory.py # Factory de clientes ComfyUI
│   ├── job_router.py             # Routing de jobs
│   ├── queue_service.py          # Estado de cola
│   ├── job_scheduler.py          # Scheduler loop
│   ├── plan_limits_service.py    # Limites por plan
│   ├── workflow_registry.py      # Templates de workflows
│   ├── workflow_planner.py       # Analisis de intencion
│   ├── workflow_builder.py       # Construccion de JSON
│   ├── workflow_validator.py     # Validacion
│   ├── workflow_preset_service.py # Presets de usuario
│   ├── backend_capability_service.py # Deteccion de capacidades
│   ├── user_service.py           # Gestion de usuarios
│   └── demo_service.py          # Modo demo
│
└── schemas/                        # MODELOS PYDANTIC
    ├── auth_schema.py
    ├── user_schema.py
    ├── job_schema.py
    ├── queue_schema.py
    ├── workflow_schema.py
    └── plan_schema.py
```

### Nucleo del Frontend (src_frontend/)

```
src_frontend/src/
├── api/                            # SERVICIOS API
│   ├── client.ts                 # Axios instance
│   ├── auth.ts                   # Auth API
│   ├── render.ts                 # Jobs API
│   ├── queue.ts                  # Queue API
│   ├── workflow.ts                # Workflows API
│   ├── plans.ts                  # Plans API
│   └── ops.ts                    # Ops API
│
├── components/                     # COMPONENTES REUTILIZABLES
│   ├── Layout.tsx                # Layout principal
│   ├── BackendStatusPanel.tsx   # Estado de backends
│   ├── QueueStatusPanel.tsx     # Panel de cola
│   ├── WorkflowPlannerPanel.tsx  # Planificador de workflows
│   ├── JobSubmitForm.tsx        # Formulario de envio
│   └── PlanBadge.tsx            # Badge de plan
│
├── pages/                         # VISTAS
│   ├── Dashboard.tsx             # Dashboard principal
│   ├── CreateJob.tsx            # Crear job
│   ├── QueuePage.tsx            # Estado de cola
│   ├── WorkflowsPage.tsx        # Catalogo de workflows
│   ├── PlansPage.tsx            # Comparativa de planes
│   ├── AdminPage.tsx            # Panel de administracion
│   └── LoginPage.tsx            # Login/Registro
│
├── hooks/                         # REACT QUERY HOOKS
│   ├── useBackend.ts           # useInstances, useCapabilities
│   ├── useJobs.ts              # useJobs, useJob, useCreateJob
│   ├── useWorkflow.ts          # useWorkflowCatalog, usePlanWorkflow
│   ├── useQueue.ts             # useQueueStatus
│   └── usePlans.ts             # usePlansCatalog, useUserPlanStatus
│
├── store/                         # ZUSTAND STORES
│   ├── authStore.ts            # Auth state
│   └── jobStore.ts             # Job creation state
│
└── types/                         # TYPE SCRIP TYPES
    ├── user.ts
    ├── job.ts
    ├── queue.ts
    ├── workflow.ts
    └── backend.ts
```

## Flujo de Datos Principal

```
1. USUARIO -> FRONTEND (CreateJob)
   └── Escribe intencion/prompt

2. FRONTEND -> BACKEND (/api/workflows/plan)
   └── Envia intencion al planner

3. BACKEND -> WORKFLOW PLANNER
   └── Analiza intencion
   └── Selecciona workflow base
   └── Detecta backend correcto

4. BACKEND -> FRONTEND (analysis)
   └── Devuelve propuesta
   └── Incluye confianza

5. USUARIO -> FRONTEND (Lanzar Job)
   └── Confirma workflow

6. FRONTEND -> BACKEND (/api/render/jobs)
   └── Crea job con plan del usuario

7. BACKEND -> QUEUE SERVICE
   └── Valida limites del plan
   └── Encola job

8. SCHEDULER -> QUEUE SERVICE
   └── Detecta slot libre
   └── Saca job de cola

9. SCHEDULER -> BACKEND COMFYUI (via comfyui_client_factory)
   └── Envia prompt al backend correcto
   └── Monitorea estado

10. BACKEND COMFYUI -> SCHEDULER
    └── Devuelve resultado

11. SCHEDULER -> QUEUE SERVICE
    └── Actualiza estado del job
    └── Libera slot

12. BACKEND -> FRONTEND (polling)
    └── Usuario ve resultado
```

## Backends ComfyUI

| Backend | Puerto | Proposito | Max Jobs |
|---------|--------|-----------|----------|
| still | 8188 | Imagenes | 2 |
| video | 8189 | Video | 1 |
| dubbing | 8190 | Audio | 2 |
| lab | 8191 | Experimental | 1 |

## Estados de Job

```
PENDING -> QUEUED -> SCHEDULED -> RUNNING -> SUCCEEDED
                                   └-> FAILED
                                   └-> TIMEOUT
                                   └-> CANCELED
```

## Proyectos Heredados

| Proyecto | Tipo | Integrar? |
|----------|------|-----------|
| CID_SERVER | Backend/API | Auditar componentes reutilizables |
| CINE_AI_PLATFORM | Plataforma | Auditar flujos de usuario |
| PROYECTO FINAL V1 | Integracion | Auditar conexiones ComfyUI |
| Web Ailink_Cinema | Frontend | Auditar componentes UI移植ables |

## Dependencias

### Backend
- fastapi
- uvicorn
- pydantic
- python-jose
- passlib
- aiohttp
- pyyaml

### Frontend
- react
- react-router-dom
- @tanstack/react-query
- axios
- zustand
- lucide-react
- tailwindcss

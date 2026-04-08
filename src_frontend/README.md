# SERVICIOS_CINE Frontend

Frontend React + TypeScript + Vite para la plataforma SERVICIOS_CINE.

## Quick Start

```bash
cd src_frontend
npm install
npm run dev
```

Abre http://localhost:3000

## Estructura

```
src/
├── api/              # Servicios API
│   ├── auth.ts       # Autenticación
│   ├── render.ts     # Jobs
│   ├── queue.ts      # Cola
│   ├── workflow.ts   # Workflows
│   ├── plans.ts      # Planes
│   └── ops.ts        # Backends/Admin
├── components/       # Componentes reutilizables
│   ├── Layout.tsx
│   ├── BackendStatusPanel.tsx
│   ├── QueueStatusPanel.tsx
│   ├── WorkflowPlannerPanel.tsx
│   ├── JobSubmitForm.tsx
│   └── PlanBadge.tsx
├── hooks/            # React Query hooks
├── pages/            # Vistas
│   ├── Dashboard.tsx
│   ├── CreateJob.tsx
│   ├── QueuePage.tsx
│   ├── WorkflowsPage.tsx
│   ├── PlansPage.tsx
│   ├── AdminPage.tsx
│   └── LoginPage.tsx
├── store/            # Zustand stores
├── types/            # TypeScript types
└── utils/            # Utilidades
```

## Rutas

- `/login` - Login/Registro
- `/` - Dashboard principal
- `/create` - Crear nuevo job
- `/queue` - Estado de cola
- `/workflows` - Catálogo de workflows
- `/plans` - Planes y precios
- `/admin` - Panel admin

## Flujo de Usuario

1. **Login** → Registro/Autenticación
2. **Dashboard** → Vista general con backends y jobs recientes
3. **Crear Job** → Seleccionar tipo → Escribir intención → Planificar → Enviar
4. **Cola** → Seguimiento de jobs en tiempo real
5. **Workflows** → Explorar templates disponibles
6. **Plans** → Ver límites del plan actual

## Dependencias

- React 18
- React Router DOM 6
- TanStack Query
- Zustand (state management)
- Lucide React (iconos)
- Tailwind CSS (estilos)

## API Endpoints Consumidos

### Auth
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me

### Jobs
- POST /api/render/jobs
- GET /api/render/jobs
- GET /api/render/jobs/{id}
- POST /api/render/jobs/{id}/retry

### Queue
- GET /api/queue/status
- GET /api/queue/status/{id}
- POST /api/queue/{id}/cancel
- POST /api/queue/{id}/retry

### Workflows
- GET /api/workflows/catalog
- POST /api/workflows/plan
- POST /api/workflows/build
- GET /api/workflows/presets
- POST /api/workflows/presets

### Plans
- GET /api/plans/catalog
- GET /api/plans/me

### Ops
- GET /api/ops/instances
- GET /api/ops/capabilities
- GET /api/admin/system/overview

## Desarrollo

```bash
# Desarrollo
npm run dev

# Build producción
npm run build

# Lint
npm run lint
```

## Configuración

El proxy de Vite está configurado para redirigir `/api` a `http://localhost:8000`.

Para cambiar el backend, edita `vite.config.ts`.

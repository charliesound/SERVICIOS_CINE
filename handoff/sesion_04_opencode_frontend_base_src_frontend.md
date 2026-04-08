# SESION 04: OpenCode - Frontend Base en src_frontend

## Rol
Senior Frontend Engineer

## Ruta de Trabajo
`D:\SERVICIOS_CINE\src_frontend`

## Contexto
Frontend React+TypeScript+Vite existente. No crear apps/web o subdirectorios innecesarios.

## Objetivo
Verificar y enhancer el frontend base:
1. Estructura de carpetas correcta
2. Proxy a backend configurado
3. Routing funcionando
4. Auth basico
5. Components principales

## Archivos Existentes a Verificar
```
src_frontend/
├── src/
│   ├── api/
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── render.ts
│   │   ├── queue.ts
│   │   ├── workflow.ts
│   │   ├── plans.ts
│   │   └── ops.ts
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── BackendStatusPanel.tsx
│   │   ├── QueueStatusPanel.tsx
│   │   ├── WorkflowPlannerPanel.tsx
│   │   ├── JobSubmitForm.tsx
│   │   └── PlanBadge.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── CreateJob.tsx
│   │   ├── QueuePage.tsx
│   │   ├── WorkflowsPage.tsx
│   │   ├── PlansPage.tsx
│   │   ├── AdminPage.tsx
│   │   └── LoginPage.tsx
│   ├── hooks/
│   ├── store/
│   ├── types/
│   └── utils/
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Tareas
1. Verificar npm install completa
2. Verificar vite.config.ts proxy a :8000
3. Probar que npm run dev levanta
4. Verificar que todas las paginas cargan

## Reglas
- NO crear apps/ o subdirectorios innecesarios
- Mantener estructura flat dentro de src/
- Usar TypeScript strict mode

## Smoke Test
```bash
cd D:\SERVICIOS_CINE\src_frontend
npm install
npm run dev
# Abrir http://localhost:3000
```

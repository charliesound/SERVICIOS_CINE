# SESION 14: OpenCode - Ops y Monitoring

## Rol
Senior Backend Engineer

## Ruta de Trabajo
`D:\SERVICIOS_CINE\src`

## Objetivo
Crear rutas y paneles para supervision operativa.

## Informacion a Devolver
- Estado general del sistema
- Instancias activas
- Trabajos en cola
- Trabajos en ejecucion
- Saturacion por backend
- Errores recientes

## Archivos a Crear/Verificar

### 1. routes/ops_routes.py (ya existe)
Verificar endpoints:
- GET /api/ops/status
- GET /api/ops/instances
- GET /api/ops/instances/{backend}
- GET /api/ops/capabilities
- POST /api/ops/health-check-all
- GET /api/ops/can-run

### 2. routes/queue_routes.py (ya existe)
Verificar:
- GET /api/queue/status

### 3. routes/admin_routes.py (ya existe)
Verificar:
- GET /api/admin/scheduler/status
- POST /api/admin/scheduler/start
- POST /api/admin/scheduler/stop
- GET /api/admin/system/overview

## Panel Admin Frontend
Verificar pagina en `src_frontend/src/pages/AdminPage.tsx`:
- Estado de backends
- Capacidades detectadas
- Jobs en cola/ejecucion
- Saturacion por backend
- Botones de control

## Smoke Test
```bash
# Status consolidado
curl http://localhost:8000/api/ops/status

# Instancias
curl http://localhost:8000/api/ops/instances

# Cola
curl http://localhost:8000/api/queue/status

# Overview
curl http://localhost:8000/api/admin/system/overview
```

## Response Example - /api/ops/status
```json
{
  "timestamp": "2026-04-06T12:00:00",
  "overall_status": "healthy",
  "summary": {
    "total_backends": 4,
    "available_backends": 4,
    "total_running": 3,
    "total_queued": 12
  },
  "backends": [
    {
      "key": "still",
      "name": "Still Image Generation",
      "healthy": true,
      "current_jobs": 2,
      "max_jobs": 5,
      "saturation_percent": 40.0
    }
  ]
}
```

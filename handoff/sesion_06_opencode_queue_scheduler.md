# SESION 06: OpenCode - Queue y Scheduler

## Rol
Senior Backend Engineer

## Ruta de Trabajo
`D:\SERVICIOS_CINE\src`

## Objetivo
Implementar sistema de cola y scheduler para control de concurrencia.

## Reglas de Concurrencia
- still: max 2 jobs simultaneos
- video: max 1 job simultaneo
- dubbing: max 2 jobs simultaneos
- lab: max 1 job simultaneo (solo admin)

## Estados de Job
- queued -> scheduled -> running -> succeeded/failed/timeout
- + canceled, rejected

## Archivos a Crear/Verificar

### 1. services/queue_service.py (ya existe)
Verificar que incluye:
- QueueStatus enum
- QueueItem dataclass
- QueueService singleton
- enqueue(), get_status(), get_all_status()
- mark_running(), mark_succeeded(), mark_failed()

### 2. services/job_scheduler.py (ya existe)
Verificar que incluye:
- JobScheduler singleton
- start(), stop()
- _run_loop() con poll interval
- _process_queues()
- _check_timeouts()

### 3. routes/queue_routes.py (ya existe)
Verificar endpoints:
- GET /api/queue/status
- GET /api/queue/status/{job_id}
- POST /api/queue/{job_id}/cancel
- POST /api/queue/{job_id}/retry

## Flujo Esperado
1. POST /api/render/jobs -> job entra a cola como "queued"
2. Scheduler detecta slot libre -> job pasa a "running"
3. Job termina -> pasa a "succeeded" o "failed"
4. Scheduler detecta timeout -> job pasa a "timeout"

## Smoke Test
```bash
# Crear job
curl -X POST http://localhost:8000/api/render/jobs \
  -H "Content-Type: application/json" \
  -d '{"task_type":"still","workflow_key":"test","prompt":{},"user_id":"u1","user_plan":"free"}'

# Ver cola
curl http://localhost:8000/api/queue/status

# Ver job especifico
curl http://localhost:8000/api/queue/status/{job_id}
```

## Notas
- Usar store en memoria para V1 (sin Redis)
- Scheduler corre en asyncio loop
- Poll interval: 5 segundos
- Timeout default: 3600 segundos

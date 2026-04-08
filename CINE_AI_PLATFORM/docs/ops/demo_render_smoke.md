# Demo render smoke (polling + retry)

## Precondiciones
- Stack demo levantado (`api` + `web`) en WSL.
- `COMFYUI_BASE_URL` configurado (puede fallar; smoke debe detectarlo).
- URL base:

```bash
export DEMO_URL="http://localhost:8080"
```

## 1) Crear job

```bash
curl -s -X POST "$DEMO_URL/api/render/jobs" \
  -H "Content-Type: application/json" \
  -d '{"request_payload":{"prompt":{"1":{"class_type":"KSampler","inputs":{}}}}}'
```

Guardar `job.job_id`.

Tiempo esperable create: <1 s.

## 2) Consultar estado del job (poll manual)

```bash
curl -s "$DEMO_URL/api/render/jobs/<job_id>"
```

Repetir hasta estado terminal (`succeeded|failed|timeout`).

Tiempo esperable de cierre:
- ComfyUI reachable: 1-6 s
- Timeout: `COMFYUI_TIMEOUT_SECONDS + overhead` (~1 s)

## 3) Listado de jobs

```bash
curl -s "$DEMO_URL/api/render/jobs?limit=10"
```

## Criterios de estado

### succeeded (real)
- finalizacion verificada por history de ComfyUI
- `result.completion_source="history"`
- `duration_ms` presente

### failed
- error manejable de submit/history/payload
- `error.code` y `error.message` presentes

### timeout
- no hay finalizacion verificable dentro del timeout
- `error.code=COMFYUI_TIMEOUT`

## 4) Retry minimo
Permitido solo para jobs `failed` o `timeout`.

```bash
curl -s -X POST "$DEMO_URL/api/render/jobs/<job_id>/retry"
```

Respuesta: nuevo job `queued` con `parent_job_id=<job_id_origen>`.

## 5) Inspeccionar persistencia
SQLite:
- local: `apps/api/data/render_jobs.db`
- contenedor: `/app/data/render_jobs.db`

```bash
sqlite3 apps/api/data/render_jobs.db "SELECT job_id,parent_job_id,status,created_at,updated_at,duration_ms FROM render_jobs ORDER BY created_at DESC LIMIT 20;"
```

## Fallback demo sin ComfyUI
Si jobs terminan en `failed`/`timeout`:
1. mostrar `GET /api/ops/status`
2. continuar demo en flujo storage/editor
3. omitir render en vivo hasta recuperar ComfyUI

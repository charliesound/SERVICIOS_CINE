# Lifecycle de render jobs (Sprint 6)

## Flujo de estados actualizado

```text
POST /api/render/jobs
    -> queued
    -> running
       -> submit a ComfyUI (/prompt) -> prompt_id
       -> poll ComfyUI history (/history/{prompt_id})
          -> succeeded  (history confirma finalizacion)
          -> failed     (history/error o fallo no-timeout)
          -> timeout    (sin finalizacion dentro del timeout)

POST /api/render/jobs/{job_id}/retry
    -> nuevo job queued (parent_job_id = job_id origen)
    -> running -> succeeded|failed|timeout
```

## Transiciones validas
- `queued -> running`
- `running -> succeeded`
- `running -> failed`
- `running -> timeout`

No hay transiciones inversas en este sprint.

Retry no muta el job original; crea uno nuevo enlazado.
Retry solo se permite si el job origen esta en `failed` o `timeout`.

## Reglas de decision por estado final

### `succeeded`
- `prompt_id` obtenido en submit
- polling a `history` detecta finalizacion verificable para ese `prompt_id`
- se persiste `result` con evidencia minima de history

### `failed`
- payload invalido para submit
- error HTTP no-timeout en ComfyUI
- history devuelve error/estado no valido para cierre exitoso

### `timeout`
- se agota `COMFYUI_TIMEOUT_SECONDS` sin evidencia de finalizacion en history

## Eventos por fase

### queued
- persistir job inicial
- responder `201` con `job_id`

### running
- marcar inicio de ejecucion
- limpiar error previo
- submit + polling/history

### succeeded
- persistir `comfyui_prompt_id`
- persistir `result` minimo normalizado
- persistir `duration_ms`

### failed / timeout
- persistir `error.code` y `error.message` (details opcional)
- persistir `duration_ms`

## Reglas operativas
- ComfyUI es opcional: su fallo no tumba API.
- Jobs siempre inspeccionables por `/api/render/jobs*`.
- Persistencia local SQLite en `RENDER_JOBS_SQLITE_FILE`.

## Limitaciones vigentes
- Sin worker distribuido o cola externa.
- Sin descarga/gestor de media final.
- Verificacion de finalizacion depende de polling minimo sobre `history`.

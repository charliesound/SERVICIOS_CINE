# Contrato real minimo Jobs/Render (Sprint 6)

## Objetivo
Definir un contrato MVP de jobs/render donde `succeeded` signifique finalizacion minimamente verificada contra ComfyUI (no solo prompt aceptado).

## Que es un render job
Un render job representa una solicitud de render enviada por backend a ComfyUI externo, con estado persistido en SQLite y resultado/error inspeccionable.

## Estados validos
- `queued`
- `running`
- `succeeded`
- `failed`
- `timeout`

## Significado operativo de cada estado
- `queued`: job creado y persistido, aun sin ejecucion efectiva.
- `running`: backend ya envio prompt a ComfyUI y esta verificando finalizacion via polling.
- `succeeded`: ComfyUI reporta finalizacion verificable en `history` para ese `prompt_id`.
- `failed`: error funcional o tecnico no-timeout (payload invalido, HTTP error, history con error, etc.).
- `timeout`: no se obtuvo finalizacion verificable dentro de ventana de timeout.

## Diferencia clave: prompt aceptado vs finalizacion verificada
- **Prompt aceptado**: `POST /prompt` devuelve `prompt_id`.
- **Finalizacion verificada**: `GET /history/{prompt_id}` devuelve evidencia de ejecucion completada.
- En Sprint 6, `succeeded` debe mapear al segundo caso.

## Campos minimos persistidos por job
- `job_id` (string, UUID)
- `created_at` (ISO datetime)
- `updated_at` (ISO datetime)
- `status` (enum)
- `request_payload` (objeto JSON)
- `parent_job_id` (string opcional, vinculo de retry)
- `comfyui_prompt_id` (string opcional)
- `result` (objeto JSON opcional)
- `error` (objeto JSON opcional)
- `duration_ms` (int opcional)

## Endpoints minimos expuestos

### Crear job
- `POST /api/render/jobs`

Payload minimo:

```json
{
  "request_payload": {
    "prompt": {
      "1": {
        "class_type": "KSampler",
        "inputs": {}
      }
    }
  }
}
```

### Listar jobs
- `GET /api/render/jobs`
- query opcional: `limit` (1..200, default 50)

### Consultar job
- `GET /api/render/jobs/{job_id}`

### Retry minimo
- `POST /api/render/jobs/{job_id}/retry`
- permitido solo si job origen esta en `failed` o `timeout`
- crea un nuevo job en `queued` enlazado por `parent_job_id`

## Relacion con ComfyUI externo
- Backend usa `COMFYUI_BASE_URL` y `COMFYUI_TIMEOUT_SECONDS`.
- Flujo minimo esperado:
  1. `POST /prompt`
  2. polling `GET /history/{prompt_id}`
  3. cierre en `succeeded|failed|timeout`
- ComfyUI permanece fuera de Docker y no se expone directamente.

## Comportamiento degradado
- Si ComfyUI no responde o no finaliza a tiempo:
  - el job termina en `failed` o `timeout`
  - se persiste `error` con codigo manejable
  - la API sigue operativa (`/api/health`, `/api/storage/*`, `/api/render/jobs*`)

## Compatibilidad con legacy
- `GET /jobs` legacy/mock se mantiene temporalmente.
- Contrato oficial de render job: `/api/render/jobs*`.

## Ejemplo esperado de job exitoso (finalizacion verificada)

```json
{
  "ok": true,
  "job": {
    "job_id": "9f8f0a3e-8a8e-4b92-a8c6-661e811f5b0d",
    "created_at": "2026-03-31T10:10:00+00:00",
    "updated_at": "2026-03-31T10:10:03+00:00",
    "status": "succeeded",
    "request_payload": {"prompt": {}},
    "parent_job_id": null,
    "comfyui_prompt_id": "12345",
    "result": {
      "provider": "comfyui",
      "prompt_id": "12345",
      "completion_source": "history",
      "history_summary": {
        "has_outputs": true
      }
    },
    "error": null,
    "duration_ms": 2450
  }
}
```

## Ejemplo esperado de timeout

```json
{
  "ok": true,
  "job": {
    "job_id": "fe79e4e2-a4f2-4a75-8f6b-9a35f7d8e3d9",
    "status": "timeout",
    "parent_job_id": null,
    "error": {
      "code": "COMFYUI_TIMEOUT",
      "message": "ComfyUI did not report completion in time",
      "details": null
    },
    "duration_ms": 2500
  }
}
```

## Ejemplo de retry

```json
{
  "ok": true,
  "job": {
    "job_id": "1f5f3437-3e97-4a85-b4cf-ef9f97c52320",
    "created_at": "2026-03-31T10:20:00+00:00",
    "updated_at": "2026-03-31T10:20:00+00:00",
    "status": "queued",
    "parent_job_id": "fe79e4e2-a4f2-4a75-8f6b-9a35f7d8e3d9",
    "request_payload": {"prompt": {}},
    "comfyui_prompt_id": null,
    "result": null,
    "error": null,
    "duration_ms": null
  }
}
```

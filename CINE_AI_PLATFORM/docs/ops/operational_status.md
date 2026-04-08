# Estado operativo en demo

## Endpoint recomendado
- `GET /api/ops/status`

Endpoints render MVP de apoyo:
- `POST /api/render/jobs`
- `GET /api/render/jobs`
- `GET /api/render/jobs/{job_id}`
- `POST /api/render/jobs/{job_id}/retry`

Ejemplo local:

```bash
curl -s http://localhost:8080/api/ops/status
```

## Que refleja
- `ok`: estado general de salud activa de storage backend.
- `mode`: entorno actual (`app_env`).
- `storage_backend`: backend activo (`json`/`sqlite`).
- `legacy_routes_enabled`: legacy on/off.
- `comfyui.configured` y `comfyui.reachable` (opcional).
- `checks`: salud de json/sqlite.

## Lectura rapida durante demo
- `ok=true` + `comfyui.reachable=true`: demo completa.
- `ok=true` + `comfyui.reachable=false`: demo degradada sin render, continuar con storage/editor.
- `ok=false`: recuperar API antes de continuar.

## Seguridad
- El endpoint no expone secretos.
- Solo muestra estado operativo y flags de entorno.

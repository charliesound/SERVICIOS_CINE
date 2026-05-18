# Objetivo

Habilitar el primer tramo de render real ComfyUI desde CID reutilizando la cola durable y el registry unificado, sin tocar frontend ni workflows crudos.

## Contexto

- El backend ya tenia `POST /api/render/jobs`, `queue_service`, `job_scheduler`, `workflow_builder` y tracking en `project_jobs` / `media_assets`.
- El gap real estaba en la persistencia final: el scheduler guardaba solo URLs remotas de ComfyUI `/view`, sin descargar el archivo al storage seguro del tenant.
- La resolucion de instancia operativa ya estaba consolidada en `services.instance_registry` + `src/config/instances.yml` con overrides por env.

## Archivos afectados

- `src/routes/render_routes.py`
- `src/services/job_tracking_service.py`
- `src/services/comfyui_storyboard_render_service.py`
- `src/services/comfyui_workflow_template_service.py`
- `src/services/comfyui_workflow_catalog_service.py`
- `src/comfyui_workflows/cinematic_storyboard_sdxl.template.json`
- `src/comfyui_workflows/storyboard_fast_sdxl.template.json`
- `tests/unit/test_render_routes_error_handling.py`
- `tests/unit/test_comfyui_instance_routing.py`
- `scripts/smoke_comfyui_real_render_guard.py`

## Entradas

- `task_type` y `workflow_key` del render job.
- Registry unificado de instancias (`instances.yml` + env overrides).
- Historial de outputs devuelto por ComfyUI (`/history/{prompt_id}`).

## Salidas

- `POST /api/render/jobs` responde `202 Accepted` con `job_id`.
- Assets finales descargados a `storage_output_dir/renders/<org>/<project>/<job_id>/...`.
- `media_assets` queda con `canonical_path`, `relative_path`, `content_ref=file://...` y metadata de origen remoto.
- Thumbnail local `.webp` de 256px cuando Pillow esta disponible y el asset es imagen.

## Flujo de trabajo

1. El endpoint valida auth existente y encola el trabajo.
2. `job_scheduler` envia el prompt real a ComfyUI usando el backend resuelto por registry.
3. Al completarse `/history/{prompt_id}`, `job_tracking_service.persist_scheduler_success_assets()` descarga cada output desde `/view`.
4. El archivo se guarda en storage local tenant-safe y se registra en `media_assets`.
5. Si aplica, se genera thumbnail webp local para consumo posterior.
6. Los storyboards SDXL se compilan desde templates API (`*.template.json`) y no desde exports raw de UI (`{"nodes": [...]}`), para que ComfyUI reciba nodos `class_type` validos.

## Validaciones

- `python -m compileall src/core src/routes src/services src/schemas src/middleware src/dependencies src/models`
- `python -m pytest tests/unit/test_render_routes_error_handling.py -q`
- `python -m pytest tests/unit/test_comfyui_instance_routing.py -q`
- `python -m pytest tests/unit/ -q`
- `python -m pytest tests/integration/ -q`
- `alembic heads`

## Casos borde

- ComfyUI responde `/prompt` pero falla `/view`: el job debe quedar fallido con error explicito.
- Overrides `COMFYUI_STILL_BASE_URL` deben dominar sobre YAML para `storyboard` y `still`.
- Assets no imagen no deben intentar thumbnail.
- Sin Pillow instalado, la persistencia del asset sigue siendo valida y solo se omite el thumbnail.
- Si un workflow del catalogo apunta a un export raw de UI, `compiled_workflow_preview` fallara aunque el workflow exista en disco.

## Restricciones conocidas

- No se introducen migraciones nuevas.
- No se altera el contrato legacy `/api/v1/comfyui/*`.
- No se cambia routing global de puertos; se usa registry/env existente.

## Errores aprendidos

- Guardar solo `backend /view` como `content_ref` no alcanza para tenancy-safe previews ni para resiliencia ante rotacion de outputs remotos.
- Mantener `200 OK` en un endpoint async de cola dificulta distinguir enqueue de ejecucion real; `202` deja el contrato mas claro sin romper el body.
- El root cause del bloqueo real en storyboard SDXL fue mapear `cinematic_storyboard_sdxl` al archivo raw `cinematic_storyboard_sdxl.json` en vez del template API `cinematic_storyboard_sdxl.template.json`; la validacion buscaba `class_type` y por eso reportaba nodos base faltantes.

## Comandos seguros

- `git status --short`
- `python -m pytest tests/unit/test_render_routes_error_handling.py -q`
- `python -m pytest tests/unit/test_comfyui_instance_routing.py -q`
- `python scripts/smoke_comfyui_real_render_guard.py --render`

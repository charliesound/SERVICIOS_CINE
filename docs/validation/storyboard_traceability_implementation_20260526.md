# STORYBOARD.TRACE.2 - Implementacion minima de trazabilidad storyboard

Fecha: 2026-05-26

## Archivos creados

- `src/schemas/storyboard_trace_schema.py`
- `src/services/storyboard_trace_service.py`
- `tests/unit/test_storyboard_trace_service.py`
- `tests/unit/test_storyboard_trace_routes.py`
- `tests/unit/test_storyboard_asset_repair_service.py`

## Archivos modificados

- `src/routes/storyboard_routes.py`
- `src/services/storyboard_asset_repair_service.py`
- `src_frontend/src/types/storyboard.ts`
- `src_frontend/src/api/storyboard.ts`
- `src_frontend/src/components/storyboard/ShotCard.tsx`

## Endpoints anadidos

- `GET /api/projects/{project_id}/storyboard/shots/{shot_id}/trace`
- `GET /api/projects/{project_id}/storyboard/trace`
- `GET /api/projects/{project_id}/storyboard/assets/{asset_id}/trace`

Los endpoints usan el contexto tenant existente y validan `project_id`/`organization_id` mediante el servicio de storyboard.

## Campos trace disponibles

- Prompt: narrativa original, prompt positivo enriquecido, prompt negativo, resumen de prompt y descripcion ES cuando existen.
- Workflow: `workflow_key`, profile requested/executed, fallback aplicado, razon de fallback, missing nodes y missing models.
- Modelo: `model_family`, `checkpoint`, LoRAs si existen, `seed`, `steps`, `cfg`, `sampler` y `scheduler` si estan persistidos.
- Render/job: `generation_job_id` y `render_job_id`.
- Asset: `media_asset_id`, nombre de archivo, tamano, MIME, URL API de thumbnail e imagen.
- Version: version actual, total inferido, indicador de versiones anteriores y lista minima de versiones previas detectables.
- Asociacion asset-shot: `association_method`, `association_confidence`, `association_reason`, `repaired_at`.

## Campos no disponibles o parciales

- Rollback: no implementado en esta fase.
- Snapshot inmutable: no implementado porque requiere persistencia nueva.
- Historial completo de versiones: solo se muestran indicios y versiones relacionadas por `project_id + sequence_id + sequence_order + scene_number`.
- Parametros ComfyUI profundos: `seed`, `steps`, `cfg`, `sampler`, checkpoint y LoRAs se exponen solo si ya existen en `StoryboardShot`, `MediaAsset` o `ProjectJob` metadata/result data.
- Usuario creador enriquecido: no se anade lookup de usuario en esta fase.

## Seguridad y sanitizacion

- El servicio no devuelve `canonical_path`.
- El servicio no devuelve `storage_path`.
- El servicio no devuelve rutas absolutas `/opt/...`, `/mnt/...`, rutas UNC ni drive letters Windows.
- Para assets visuales se devuelven URLs API autenticadas:
  - `/api/projects/{project_id}/storyboard/shots/{shot_id}/thumbnail`
  - `/api/projects/{project_id}/storyboard/shots/{shot_id}/image`
- Las pruebas validan que `/opt/`, `/mnt/`, `canonical_path` y `storage_path` no aparecen en el JSON de trace.

## UX anadida

- `ShotCard` incluye collapsible `Trazabilidad`.
- La traza se carga bajo demanda al abrir el panel.
- Se muestra:
  - prompt resumido
  - workflow key/profile
  - fallback de workflow
  - modelo/checkpoint
  - seed/steps/cfg/sampler
  - render job
  - media asset
  - version actual e indicios de versiones anteriores
- Acciones:
  - `Copiar prompt`
  - `Ver detalle tecnico`
- Si faltan datos, se muestra `No disponible` sin romper la tarjeta.

## Metadata de reparacion

`storyboard_asset_repair_service.py` ahora registra en `shot.metadata_json.asset_association`:

- `association_method`: `direct_metadata_link` o `repair_service`
- `association_confidence`
- `association_reason`
- `repaired_at`

Tambien se preserva el motivo mas fuerte de asociacion directa por `metadata_json.storyboard_shot_id` cuando existen otros matches secundarios.

## Tests y validacion

```bash
source .venv/bin/activate && python -m py_compile \
  src/schemas/storyboard_trace_schema.py \
  src/services/storyboard_trace_service.py \
  src/routes/storyboard_routes.py \
  src/routes/shot_routes.py \
  src/services/storyboard_asset_repair_service.py
```

Resultado: PASS.

```bash
PYTHONPATH=src python -m pytest tests/unit/test_storyboard_trace_service.py -q
```

Resultado: PASS. `3 passed`.

```bash
PYTHONPATH=src python -m pytest tests/unit/test_storyboard_trace_routes.py -q
```

Resultado: PASS. `3 passed`.

```bash
PYTHONPATH=src python -m pytest tests/unit/test_storyboard_asset_repair_service.py -q
```

Resultado: PASS. `2 passed`.

```bash
PYTHONPATH=src python -m pytest tests/unit/test_storyboard_*.py -q
```

Resultado: PASS. `183 passed, 141 warnings in 16.57s`.

```bash
cd /opt/SERVICIOS_CINE/src_frontend && npm run build
```

Resultado: PASS. Vite build completo con warnings existentes de dynamic import/chunk size.

```bash
git diff --check
```

Resultado: PASS. Solo warnings de line endings LF/CRLF reportados por Git.

## Riesgos pendientes

- La calidad de trace depende de metadata ya persistida por jobs/assets existentes.
- Algunos renders antiguos pueden no tener `checkpoint`, `seed`, `sampler` o `cfg` estructurados.
- La inferencia de versiones previas no sustituye un modelo de lineage persistente.
- No hay snapshot inmutable ni rollback operativo todavia.

## Siguiente fase

- Persistir snapshot de `StoryboardTraceRecord` para auditoria inmutable.
- Persistir parametros ComfyUI normalizados en `StoryboardShot`/asset metadata al completar render.
- Implementar historial visual comparativo y rollback controlado.
- Anadir metricas agregadas de trace en pantalla de proyecto si producto lo aprueba.

## Resultado

GO tecnico para commit: implementacion minima completa, tests y build verdes, sin tocar ComfyUI ni export Storyboard Sheet.

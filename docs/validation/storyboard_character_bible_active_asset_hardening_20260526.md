# STORYBOARD.CHARACTER.BIBLE.2E.1 — Active Asset Validation Hardening

## Objetivo

Refuerzo de seguridad para Character Bible: impedir que una referencia aprobada de personaje apunte a un MediaAsset inexistente, ajeno al proyecto, ajeno a la organización o no activo.

## Cambio aplicado

El endpoint de `add_reference` valida ahora que el asset pertenezca al mismo:

- `asset_id`
- `project_id`
- `organization_id`
- estado activo/indexado

Si el asset existe pero no está activo/indexado, devuelve HTTP 400 con mensaje claro.

## Seguridad

La API no expone rutas físicas internas como:

- `/opt/...`
- `/mnt/...`
- `C:\...`
- `storage_path`
- `canonical_path`

## Concurrencia

La persistencia file-backed actual sigue siendo válida para entorno single-worker.

No debe usarse en despliegues multi-worker sin una de estas soluciones:

- filelock interproceso
- Redis lock
- migración a base de datos

## Validación

Ejecutado correctamente:

- `python -m pytest tests/unit/test_character_bible_routes.py -q`
- `python -m pytest tests/unit/test_character_bible_service.py -q`
- `python -m pytest tests/unit/test_character_bible_persistence.py -q`
- `python -m pytest tests/unit/test_character_bible_openapi_routes.py -q`

## Resultado

GO para entorno actual single-worker.

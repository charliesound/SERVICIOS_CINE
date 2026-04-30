# Manual Shot Editor

## Objetivo

Abrir un nucleo minimo y seguro de mutabilidad manual del storyboard para crear, editar, reordenar y borrar shots sin romper los contratos ya congelados de Presentation, Export y Delivery.

## Inspeccion real

- El filmstrip actual se construye desde `media_assets` y `metadata_json.sequence_id/shot_order`
- Existe un modelo legacy `shots` en `models.visual`, pero no es tenant-safe, no tiene `organization_id`, no cubre narrativa ni vinculacion canonica con `media_assets`, y no se usa en las rutas actuales de Presentation
- No existe `storyboard_shots` ni un editor transaccional reutilizable en el backend principal

## Decision estructural

- Crear `storyboard_shots` como entidad canonica editable minima
- Mantener fallback completo al filmstrip actual basado en `media_assets` cuando un proyecto todavia no tenga `storyboard_shots`
- No abrir migracion Alembic en esta fase; SQLite runtime sync crea la tabla nueva en dev/smoke

## Contrato minimo

- `GET /api/projects/{project_id}/shots`
- `POST /api/projects/{project_id}/shots`
- `PUT /api/projects/{project_id}/shots/{shot_id}`
- `PUT /api/projects/{project_id}/shots/bulk-reorder`
- `DELETE /api/projects/{project_id}/shots/{shot_id}`

## Reglas

- Toda escritura valida `project.organization_id`
- `asset_id` solo se permite si pertenece al mismo `project_id`
- `bulk-reorder` es atomico y valida estado final sin duplicados de `sequence_order` por `project_id/sequence_id`
- `DELETE` solo elimina la fila editable, nunca el asset fisico
- Filmstrip, HTML y PDF reflejan `storyboard_shots` cuando existen

## Full loop esperado

- crear shots editables desde un proyecto smoke
- editar narrativa del segundo shot
- aplicar reorder `[2, 1]`
- validar reflejo en DTO y PDF
- confirmar bloqueo cross-tenant para tenant B

# Contrato jerárquico Storage API

## Alcance
Este documento define la jerarquia oficial de lectura/escritura para la familia `/api/storage/*`.

## Mapa de recursos
- `project` (activo)
- `sequence` (hijos de project)
- `scene` (hijos de sequence / project)
- `shot` (hijos de scene / sequence / project)

Relación esperada:

`project -> sequences -> scenes -> shots`

## Endpoints oficiales de jerarquía

### Nivel project
- `GET /api/storage/project`
- `PATCH /api/storage/project`

### Descendencia desde project
- `GET /api/storage/project/{project_id}/sequences`
- `GET /api/storage/project/{project_id}/scenes`
- `GET /api/storage/project/{project_id}/shots`

### Nivel sequence
- `GET /api/storage/sequences`
- `GET /api/storage/sequence/{sequence_id}`
- `GET /api/storage/sequence/{sequence_id}/scenes`
- `GET /api/storage/sequence/{sequence_id}/shots`
- `POST /api/storage/sequence`
- `PATCH /api/storage/sequence/{sequence_id}`
- `DELETE /api/storage/sequence/{sequence_id}`

### Nivel scene
- `GET /api/storage/scenes`
- `GET /api/storage/scene/{scene_id}`
- `GET /api/storage/scene/{scene_id}/shots`
- `POST /api/storage/scene`
- `PATCH /api/storage/scene/{scene_id}`
- `DELETE /api/storage/scene/{scene_id}`

### Nivel shot
- `GET /api/storage/shots`
- `GET /api/storage/shot/{shot_id}`
- `POST /api/storage/shot`
- `PATCH /api/storage/shot/{shot_id}`
- `DELETE /api/storage/shot/{shot_id}`

## Recursos complementarios en storage
- `GET /api/storage/characters`
- `GET /api/storage/character/{character_id}`
- `POST /api/storage/character`
- `PATCH|DELETE /api/storage/character/{character_id}`
- `GET /api/storage/info`
- `GET /api/storage/summary`
- `GET /api/storage/export-json`
- `POST /api/storage/import-json`
- `POST /api/storage/migrate-json-to-sqlite`
- `POST /api/storage/seed-demo`
- `POST /api/storage/reset`

## Semántica de respuesta (jerarquía)
- Si el recurso raíz no existe: `404` con `error.code` semántico (`PROJECT_NOT_FOUND`, `SEQUENCE_NOT_FOUND`, etc.).
- Si el recurso raíz existe sin hijos: `200` con colección vacía y `count: 0`.
- Errores internos: `500` con `error.code` estable por endpoint.

## Forma recomendada para respuestas de colección
- `ok: true`
- `storage.backend`
- `<root_id>` (por ejemplo `project_id`, `sequence_id`, `scene_id`)
- `<collection>`
- `count`

## Regla de integración
Nuevos consumidores (frontend, automatizaciones, agentes) deben usar esta jerarquía oficial y no las rutas legacy.

# Convenciones de respuesta API (Storage-first)

## Objetivo
Unificar el contrato consumido por frontend y automatizaciones en la familia oficial `/api/storage/*`.

## Convención oficial de éxito

### Colecciones
Formato recomendado:

```json
{
  "ok": true,
  "storage": { "backend": "sqlite" },
  "project_id": "project_001",
  "scenes": [],
  "count": 0
}
```

Claves esperadas:
- `ok`
- `storage.backend` (cuando aplica)
- id raíz contextual (`project_id`, `sequence_id`, `scene_id`, etc.)
- colección (`characters`, `sequences`, `scenes`, `shots`)
- `count`

### Entidad
Formato recomendado:

```json
{
  "ok": true,
  "storage": { "backend": "sqlite" },
  "shot": { "id": "shot_001" }
}
```

### Mutaciones
Formato recomendado:
- Create/Update: `{"ok": true, "<entity>": {...}}`
- Delete: `{"ok": true, "deleted": "<id>"}`

## Convención oficial de error
Formato recomendado para rutas oficiales:

```json
{
  "ok": false,
  "error": {
    "code": "SHOT_NOT_FOUND",
    "message": "Shot shot_001 not found"
  }
}
```

## Semántica HTTP
- `200`: lectura/mutación correcta
- `201`: creación cuando se explicite (en estado actual varias mutaciones crean con `200` por compatibilidad)
- `400`: payload inválido o modo no soportado
- `404`: recurso raíz inexistente
- `409`: colisión de IDs
- `500`: error interno

## Excepciones transitorias (compatibilidad)
- `/characters*` y `/api/shots*` pueden mantener formas históricas para no romper clientes actuales.
- `/projects`, `/scenes`, `/shots`, `/jobs` legacy no forman parte de esta convención oficial.

## Regla para nuevas integraciones
Para nuevas llamadas, usar solo `/api/storage/*` y asumir estas convenciones como contrato estable.

## Nota para render jobs MVP
- Endpoints: `/api/render/jobs*`
- Formato de exito:
  - create/get: `{"ok": true, "job": {...}}`
  - list: `{"ok": true, "jobs": [...], "count": <n>}`
- Formato de error: `{"ok": false, "error": {"code": "...", "message": "..."}}`

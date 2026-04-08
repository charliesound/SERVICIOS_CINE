# Estado de rutas API (Bloque A - Sprint 2)

## Objetivo
Definir una frontera clara entre rutas oficiales y legacy sin romper compatibilidad actual.

## Frontera oficial

### Familia oficial principal (usar en nuevas integraciones)
- `GET|POST|PATCH|DELETE /api/storage/*`

### Familia oficial de render (MVP Sprint 5)
- `POST /api/render/jobs`
- `GET /api/render/jobs`
- `GET /api/render/jobs/{job_id}`
- `POST /api/render/jobs/{job_id}/retry`

Esta es la capa canonical del backend para lectura/escritura narrativa y de storage.

### Rutas oficiales de plataforma
- `GET /api/health`
- `GET /api/health/details`
- `GET /api/ops/status`
- `GET /api/config`

## Rutas de compatibilidad (temporales, no objetivo futuro)
- `GET|POST|PUT|PATCH|DELETE /api/shots*`
- `GET|POST|PATCH|DELETE /characters*`

Se mantienen activas para no romper consumidores actuales mientras la migracion a storage se consolida.

## Rutas legacy deprecadas
- `GET /projects`
- `GET /scenes`
- `GET|PUT /shots`
- `GET|PUT /shots/{shot_id}`
- `GET /jobs`

En OpenAPI quedan marcadas con el tag `LEGACY-DEPRECATED`.

## Control de activacion legacy
- Variable: `ENABLE_LEGACY_ROUTES`
  - `true`: mantiene rutas legacy para compatibilidad.
  - `false`: desactiva routers legacy al arrancar.

## Politica de uso recomendada
- Nuevo frontend/automatizacion: **solo** `/api/storage/*`.
- Mantenimiento temporal: usar compatibilidad solo cuando no exista equivalente storage.
- No crear nuevas dependencias sobre `/projects`, `/scenes`, `/shots` legacy o `/jobs` mock.

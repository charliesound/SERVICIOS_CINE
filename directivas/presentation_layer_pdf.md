# Presentation / Filmstrip / PDF

## Estado

- `MULTI-TENANT ISOLATION = CLOSED`
- `STORAGE/EXPORT SEGREGATION = CLOSED`
- `ADMIN CONSOLIDATION = CLOSED`
- `UI/API ADMIN E2E = CLOSED`
- `FILMSTRIP RUNTIME = CLOSED`
- `ASSET PREVIEW TENANT-SAFE = CLOSED`
- `WEASYPRINT = VIABLE`
- `PDF SYNC EXPORT = CLOSED`
- `PRESENTATION SLICE = FEATURE FREEZE`

## Cierre formal del slice

El slice Presentation queda congelado en modo MVP estable. La implementacion activa reutiliza `projects`, `media_assets` y `review_comments`, expone filmstrip JSON, preview HTML y export PDF sincronico tenant-safe bajo `/api/projects/.../presentation/...` sin abrir namespaces nuevos ni colas async.

## Checklist final completado

- `GET /api/projects/{project_id}/presentation/filmstrip` devuelve DTO real desde `media_assets`
- `GET /api/projects/{project_id}/presentation/filmstrip.html` renderiza preview HTML end-to-end
- `GET /api/projects/{project_id}/presentation/assets/{asset_id}/preview` sirve preview tenant-safe
- `GET /api/projects/{project_id}/presentation/export/pdf` devuelve PDF real con WeasyPrint
- `POST /api/projects/{project_id}/presentation/export-pdf` sigue operativo como wrapper compatible
- Tenant A accede a sus recursos presentation
- Tenant B recibe `403` ante filmstrip, asset preview y PDF de tenant A
- `/health` y `/ready` siguen en `200`

## Contrato congelado MVP

- `GET /api/projects/{project_id}/presentation/filmstrip`
- `GET /api/projects/{project_id}/presentation/filmstrip.html`
- `GET /api/projects/{project_id}/presentation/assets/{asset_id}/preview`
- `GET /api/projects/{project_id}/presentation/export/pdf`
- `POST /api/projects/{project_id}/presentation/export-pdf`

## Reglas tecnicas confirmadas

- El render PDF usa `WeasyPrint`
- El renderer es sincronico y no usa cola async
- El PDF no hace self-fetch HTTP al propio backend
- Para `image/*`, el renderer solo usa `file://` local tras validacion tenant-safe previa
- Para assets no-image o no resolubles, el PDF usa placeholder textual controlado
- La plantilla usa CSS compatible con WeasyPrint y evita JS y dependencias externas

## Limites MVP

- No persiste deliverables PDF listos para descarga diferida
- No optimiza aun para lotes grandes o documentos extensos
- La smoke DB actual sigue dominada por assets `document`, no por storyboard images reales
- El wrapper `POST /presentation/export-pdf` no entrega bytes, solo compatibilidad y mensaje de migracion

## Deuda tecnica diferida

- Persistencia tenant-segregated del PDF exportado
- Smoke dedicado con assets `image/*` reales y secuencias pobladas
- Metricas y observabilidad de tiempos de render
- Politica de cache o memoizacion para exports repetidos
- Versionado/historial de exports por proyecto

## Criterio futuro para async

Mover a job async solo cuando ocurra al menos uno:

- latencia HTTP inaceptable por volumen de assets o peso de imagenes
- necesidad de persistir y reintentar exports
- necesidad de descarga diferida desde storage segregado
- necesidad de trazabilidad operacional por job y version

## Nota de congelacion

Feature freeze explicito del slice Presentation. Cualquier trabajo nuevo sobre persistencia, async jobs, deliverables historicos o layouts editoriales avanzados se considera fase posterior y no forma parte de este cierre.

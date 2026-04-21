# Deliverables Persistence

## Objetivo

Persistir el PDF de Presentation como deliverable tenant-segregated reutilizando la infraestructura real ya existente de `deliverables`, `delivery_routes` y `delivery_service`, sin rediseñar el subsistema ni abrir colas async.

## Inspeccion real del repo

- `models.delivery.Deliverable` ya modela entregables por `project_id` y `organization_id`
- `services.delivery_service` ya lista, obtiene y actualiza deliverables tenant-safe, pero su creacion actual exige `source_review_id`
- `routes.delivery_routes` ya expone listado y descarga tenant-safe de deliverables por proyecto y por `deliverable_id`
- `download_deliverable` ya resuelve `delivery_payload.file_path`, pero estaba fijado a `application/zip`
- `services.export_service` ya persiste ZIPs segregados por organizacion dentro de `exports/<organization_id>/...`
- `project_jobs` existe para flujos async, pero no es requisito para este slice porque el PDF Presentation sigue siendo sincronico

## Decision minima compatible

- Mantener `GET /api/projects/{project_id}/presentation/export/pdf` como descarga directa sin persistencia obligatoria
- Anadir `POST /api/projects/{project_id}/presentation/export/pdf/persist`
- Reutilizar `deliverables` para registrar el PDF persistido
- Reutilizar `routes.delivery_routes` para listar y descargar el artefacto ya persistido
- Extender `delivery_service` con una creacion minima para deliverables basados en archivo de proyecto, sin `source_review_id`
- Extender `list_deliverables` con filtro opcional `format_type`
- Ajustar `download_deliverable` para respetar `mime_type` dinamico desde `delivery_payload`

## Convencion del artefacto

- `format_type = PRESENTATION_PDF`
- `mime_type = application/pdf`
- ruta fisica: `exports/<organization_id>/presentation_pdf/<timestamp>_<uuid>_<filename>.pdf`
- `delivery_payload` debe incluir como minimo:
  - `file_path`
  - `file_name`
  - `file_size`
  - `mime_type`
  - `category = presentation_pdf`
  - `generated_at`

## Limites MVP

- sin job async
- sin versionado avanzado
- sin cache global
- sin persistencia adicional en `project_jobs`
- sin tocar billing/reporting

## Criterio futuro

Promover a flujo async solo si el volumen de PDFs o imagenes hace inviable el request sincronico o si se exige historial/reintento formal de exports.

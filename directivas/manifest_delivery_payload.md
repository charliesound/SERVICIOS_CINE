# Manifest Delivery Payload

## Objetivo

Enriquecer el `delivery_payload` del deliverable `PRESENTATION_PDF` con un manifest/resumen headless y estable derivado del DTO real del filmstrip, sin redisenar `delivery` ni abrir nuevos bloques funcionales.

## Decision minima compatible

- Reutilizar `presentation_service.build_filmstrip(...)` como fuente unica del manifest
- Mantener `POST /api/projects/{project_id}/presentation/export/pdf/persist` como punto de persistencia
- Anadir al `delivery_payload`:
  - `manifest_summary`
  - `manifest_file_path`
  - `manifest_file_name`
  - `manifest_mime_type`
- Persistir un archivo hermano `manifest.json` junto al PDF cuando se genera el deliverable

## Esquema minimo estable

- `project_id`
- `organization_id`
- `project_name`
- `generated_at`
- `sequences_count`
- `shots_count`
- `orphan_assets_count`
- `comments_count`
- `sequence_ids`
- `asset_ids`
- `format_version`
- `source_endpoint`
- `pdf_file_name`
- `pdf_mime_type`

## Reglas

- El manifest deriva del DTO ya cerrado del slice Presentation
- El manifest fisico vive en storage segregado por `organization_id`
- Tenant B no debe poder acceder al deliverable ni a su manifest por las rutas ya existentes
- No se crean tablas nuevas ni jobs async

## Uso esperado

- B2B/headless listing: leer `manifest_summary` desde `GET /api/delivery/projects/{project_id}/deliverables`
- Auditoria operativa: usar `manifest_file_path` si se necesita inspeccion local o procesos batch posteriores

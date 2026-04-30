# PROJECT PRIVATE DOCUMENT SOURCES MVP

## Objetivo
- Permitir upload documental privado por proyecto y organizacion con aislamiento tenant-safe.
- Persistir texto extraido y metadata suficiente para una futura capa RAG.
- Mantener este bloque limitado a upload, extraction, listing, detail, delete y download.

## Alcance cerrado
- Tipos soportados: `pdf`, `docx`, `txt`.
- Estados: `pending`, `processing`, `completed`, `error`.
- Tipos documentales: `script`, `budget`, `contract`, `treatment`, `finance_plan`, `other`.
- Visibilidad: `project`, `organization_private`.

## Modelo minimo
- `project_documents`
- Campos:
  - `id`
  - `project_id`
  - `organization_id`
  - `uploaded_by_user_id`
  - `document_type`
  - `upload_status`
  - `file_name`
  - `mime_type`
  - `file_size`
  - `storage_path`
  - `checksum`
  - `extracted_text`
  - `visibility_scope`
  - `error_message`
  - `created_at`
  - `updated_at`

## Storage isolation
- Root configurable: `PROJECT_DOCUMENT_STORAGE_ROOT`.
- Convencion: `{root}/{organization_id}/{project_id}/documents/`.
- Nombre seguro, checksum SHA-256 y hard delete real en DB + storage.
- Nunca se comparte storage entre tenants.

## Endpoints
- `POST /api/projects/{project_id}/documents`
- `GET /api/projects/{project_id}/documents`
- `GET /api/projects/{project_id}/documents/{document_id}`
- `GET /api/projects/{project_id}/documents/{document_id}/download`
- `DELETE /api/projects/{project_id}/documents/{document_id}`

## Seguridad
- JWT obligatorio.
- Validacion de ownership por `project_id + organization_id`.
- Tenant B no accede a documentos de A.

## Preparado para futuro
- `extracted_text` persistido.
- `checksum`, `storage_path`, `document_type` y `visibility_scope` normalizados.
- Sin embeddings, pgvector ni retrieval semantico en esta fase.

## Validacion esperada
- Upload ok.
- List/detail ok.
- Extracted text persistido.
- Delete elimina DB + archivo.
- Tenant isolation confirmada.

## Metadata
- created: 2026-04-22
- status: MVP
- owner: backend/data architecture

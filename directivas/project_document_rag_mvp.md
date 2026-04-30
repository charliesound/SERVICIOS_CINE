# PROJECT DOCUMENT RAG MVP

## Objetivo
- Convertir `ProjectDocument.extracted_text` en una base semantica consultable por proyecto y tenant.
- Habilitar chunking, embeddings, reindex y retrieval seguro para grounding futuro.
- Mantener compatibilidad con SQLite local y dejar la arquitectura vector-ready para PostgreSQL/pgvector.

## Decision de infraestructura
- Persistencia MVP portable: `document_chunks.embedding_payload` serializado en JSON.
- Retrieval actual: similitud en aplicacion sobre chunks filtrados en SQL por `organization_id + project_id`.
- Proveedor de embeddings desacoplado y configurable; default estable `local_hash`.
- La capa queda preparada para una futura estrategia pgvector sin bloquear el entorno actual.

## Modelo minimo
- `document_chunks`
- Campos:
  - `id`
  - `document_id`
  - `project_id`
  - `organization_id`
  - `chunk_index`
  - `chunk_text`
  - `chunk_tokens_estimate`
  - `embedding_payload`
  - `metadata_json`
  - `created_at`

## Metadata util
- `document_type`
- `file_name`
- `checksum`
- `visibility_scope`
- referencia estable a documento y orden del chunk

## Pipeline MVP
- Upload/extraction documental produce `extracted_text`.
- Sobre `extracted_text`:
  - normalizacion
  - chunking configurable
  - overlap moderado
  - embedding por chunk
  - persistencia transaccional de chunks

## Retrieval
- Query embedding con el mismo proveedor.
- Filtrado efectivo en SQL por `project_id` y `organization_id` antes del ranking.
- Respuesta minima:
  - chunks relevantes
  - score
  - `document_id`
  - `file_name`
  - metadata util

## Endpoints MVP
- `POST /api/projects/{project_id}/documents/reindex`
- `GET /api/projects/{project_id}/documents/{document_id}/chunks`
- `POST /api/projects/{project_id}/ask`

## Seguridad
- JWT obligatorio.
- Ownership check por proyecto.
- Tenant B nunca puede reindexar ni consultar chunks de tenant A.

## Fuera de alcance
- pgvector obligatorio
- dashboards
- conectores externos
- matcher financiero documental
- embeddings gestionados costosos por defecto
- generacion avanzada si retrieval no esta firme

## Metadata
- created: 2026-04-22
- status: MVP
- owner: principal ai/backend

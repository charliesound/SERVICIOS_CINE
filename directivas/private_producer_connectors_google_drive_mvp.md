# PRIVATE PRODUCER CONNECTORS MVP - GOOGLE DRIVE FIRST

## Objetivo
- Permitir una conexion Google Drive tenant-safe por organizacion.
- Vincular carpetas concretas de Drive a proyectos locales.
- Sincronizar incrementalmente documentos compatibles hacia el pipeline ya existente `Google Drive -> ProjectDocument -> extracted_text -> document_chunks`.

## Inspeccion real de base
- `project_documents` ya existe y cubre upload/list/detail/download/delete con `organization_id + project_id`.
- La extraccion actual vive en `project_document_service` y soporta `pdf`, `docx` y `txt`.
- El RAG actual vive en `project_document_rag_service` y reindexa por documento reutilizando `document_chunks`.
- El control tenant-safe actual se apoya en `get_tenant_context` y en filtros SQL por `organization_id`.
- No hay Celery/Redis operativo para este bloque; el repo expone scheduler/queue propios orientados a render, no a documentos.
- No existia una capa previa de cifrado at-rest especifica para tokens externos; se incorpora cifrado simetrico derivado de secretos de app.

## Alcance cerrado
- OAuth2 Google Drive read-only.
- Conexion por tenant.
- Exploracion basica de carpetas.
- Link carpeta -> proyecto.
- Sync incremental read-only.
- Sin edicion remota.
- Sin delete bidireccional.
- Sin Dropbox, CRM, billing ni matcher v3.

## Modelo minimo
- `integration_connections`
- `integration_tokens`
- `project_external_folder_links`
- `external_document_sync_state`

## Decisiones estructurales
- No se mete logica en `Organization`; se modela una capa transversal de conectores preparada para futuros providers.
- El callback OAuth valida `state` firmado con `organization_id`, `user_id`, `nonce` y expiracion corta.
- Los tokens se almacenan cifrados at-rest y nunca se registran en logs.
- El sync reutiliza `project_document_service.import_document_bytes` para evitar un pipeline documental paralelo.
- El refresh de token ocurre bajo demanda antes de browse/sync si el access token esta vencido.

## Endpoints MVP
- `GET /api/integrations/google-drive/connect`
- `GET /api/integrations/google-drive/callback`
- `GET /api/integrations/google-drive/status`
- `POST /api/integrations/google-drive/disconnect`
- `GET /api/projects/{project_id}/integrations/google-drive/folders`
- `POST /api/projects/{project_id}/integrations/google-drive/link-folder`
- `GET /api/projects/{project_id}/integrations/google-drive/link-folder`
- `DELETE /api/projects/{project_id}/integrations/google-drive/link-folder/{link_id}`
- `POST /api/projects/{project_id}/integrations/google-drive/sync`
- `GET /api/projects/{project_id}/integrations/google-drive/sync-status`

## Sync MVP
- Lista archivos de la carpeta vinculada.
- Filtra `pdf`, `docx`, `txt`.
- Compara por `external_file_id`, `external_modified_time` y checksum externo si existe.
- Descarga solo nuevos o modificados.
- Reimporta sobre el mismo `ProjectDocument` cuando ya existe uno ligado.
- Actualiza `external_document_sync_state` y deja evidencia de archivos stale via `last_seen_at`.

## Seguridad
- Todos los accesos filtran por `organization_id` y `project_id`.
- Tenant B no puede ver ni operar conexiones, links ni sync state de A.
- Los tokens se guardan cifrados usando clave derivada de secretos de entorno.
- No se exponen tokens ni metadatos sensibles en respuestas.

## Validacion esperada
- OAuth mockeable por cliente Google aislado.
- Conexion creada por tenant.
- Link de carpeta por proyecto.
- Sync incremental con nuevo documento y reimport sobre documento existente.
- Reutilizacion comprobable de `ProjectDocument` + RAG.
- No regresion de upload manual y consulta RAG.

## Metadata
- created: 2026-04-23
- status: MVP
- owner: principal backend/integration architecture

## Runtime real closure
- OAuth real Google Drive completado con cuenta real.
- GET /api/integrations/google-drive/status => connected=true
- external_account_email = cid.jcc@gmail.com
- Se creó proyecto real para el tenant smoke_admin:
  - project_id = 97963a789c5743b0ac29c1ed6096f192
  - organization_id = ddd220ec536d4295970313ec4fe1583e
- Folder browse real:
  - count = 3
  - carpeta vinculada:
    - external_folder_id = 1oJo-_jrfLO2jLlSHTHU2oeQbCmczzMNZ
    - external_folder_name = n8n
- Link folder real:
  - link id = 444d965f-1b5a-448f-87fb-df2f1bd1056c
- Primer sync real:
  - status = completed_with_errors
  - imported = 2
  - updated = 0
  - skipped = 0
  - errors = 2
  - stale = 0
- Sync status real:
  - count states = 4
  - 2 documentos enlazados a ProjectDocument
  - 2 entradas no enlazadas
- Segundo sync real:
  - status = completed
  - imported = 0
  - updated = 0
  - skipped = 4
  - errors = 0
- Persistencia documental real:
  - ProjectDocument contiene 2 PDFs del proyecto
  - upload_status = completed
  - extracted_text presente
- RAG real:
  - document_chunks count = 65
- Nota técnica: 2 archivos importados y 2 detectados no enlazados (por ejemplo, imágenes u otros tipos no soportados), sin bloquear el cierre MVP.

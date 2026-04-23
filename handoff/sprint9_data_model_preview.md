# Sprint 9 - Data Model Preview

## Objetivo

Previsualizacion de tablas MVP para alinear backend/frontend antes de implementar.
Modelo pensado para SQLite actual, compatible con migracion posterior a Postgres.

## Convenciones comunes

- PK: `id` (string uuid)
- Scope: `organization_id`, `project_id`
- Auditoria: `created_at`, `updated_at`, `created_by`, `updated_by`
- Estados: string controlado por schema (enum logico)

## 1) Ingesta federada

### storage_sources

- id
- organization_id
- project_id
- name
- source_type (`local_mounted_path|smb_mounted_path|nfs_mounted_path|sftp|webdav`)
- root_path
- config_json
- status (`draft|validated|authorized|revoked|error`)
- is_active
- last_validated_at
- last_validation_message
- created_at/updated_at/created_by/updated_by

Indices sugeridos:

- (organization_id, project_id)
- (organization_id, status)
- unique (organization_id, name)

### storage_authorizations

- id
- organization_id
- project_id
- storage_source_id (FK storage_sources.id)
- consent_status (`pending|authorized|revoked|expired`)
- consent_text_version
- scope_paths_json
- granted_by_user_id
- granted_at
- expires_at
- revoked_by_user_id
- revoked_at
- reason
- created_at/updated_at/created_by/updated_by

Indices sugeridos:

- (storage_source_id, consent_status)
- (organization_id, expires_at)

### storage_watch_paths

- id
- organization_id
- project_id
- storage_source_id (FK storage_sources.id)
- watch_path
- recursive
- include_patterns_json
- exclude_patterns_json
- is_enabled
- last_cursor
- created_at/updated_at/created_by/updated_by

Indices sugeridos:

- unique (storage_source_id, watch_path)
- (organization_id, project_id, is_enabled)

### ingest_scans

- id
- organization_id
- project_id
- storage_source_id (FK storage_sources.id)
- watch_path_id (FK storage_watch_paths.id, nullable)
- scan_type (`manual|polling`)
- status (`queued|running|completed|failed|cancelled`)
- started_at
- finished_at
- files_seen
- files_indexed
- files_skipped
- error_message
- triggered_by_user_id
- created_at/updated_at/created_by/updated_by

Indices sugeridos:

- (organization_id, project_id, status, started_at)
- (storage_source_id, started_at)

### media_assets

- id
- organization_id
- project_id
- storage_source_id (FK storage_sources.id)
- watch_path_id (FK storage_watch_paths.id, nullable)
- scan_id (FK ingest_scans.id, nullable)
- relative_path
- filename
- extension
- mime_type
- size_bytes
- checksum_sha256
- modified_at_source
- asset_kind (`video|audio|image|document|other`)
- classification_status (`unclassified|classified|needs_review`)
- review_status (`pending|approved|rejected`)
- scene_id (nullable)
- shot_id (nullable)
- take_id (nullable)
- metadata_json
- archived_at (nullable)
- created_at/updated_at/created_by/updated_by

Indices sugeridos:

- unique (storage_source_id, relative_path, modified_at_source, size_bytes)
- (organization_id, project_id, asset_kind)
- (project_id, scene_id, shot_id, take_id)

### asset_links

- id
- organization_id
- project_id
- media_asset_id (FK media_assets.id)
- link_type (`sequence|scene|shot|take|project_asset`)
- target_id
- confidence_score
- source (`manual|heuristic|ai`)
- is_primary
- created_at/updated_at/created_by/updated_by

Indices sugeridos:

- (media_asset_id, link_type)
- (organization_id, project_id, target_id)

### ingest_events

- id
- organization_id
- project_id
- entity_type (`storage_source|authorization|watch_path|scan|asset|document|report`)
- entity_id
- event_type
- severity (`info|warning|error`)
- payload_json
- actor_user_id
- created_at

Indices sugeridos:

- (organization_id, project_id, created_at)
- (entity_type, entity_id, created_at)

## 2) Documental

### document_assets

- id
- organization_id
- project_id
- media_asset_id (FK media_assets.id, nullable)
- storage_source_id (FK storage_sources.id, nullable)
- scan_id (FK ingest_scans.id, nullable)
- original_filename
- source_path
- extension
- mime_type
- format_group (`image|pdf|doc|text|table|other`)
- status (`registered|extracted|classified|structured|pending_review|approved|rejected|archived`)
- detected_document_type (`camera_report|sound_report|script_note|director_note|operator_note|unknown_document`)
- file_size_bytes
- checksum_sha256
- created_at/updated_at/created_by/updated_by

### document_extractions

- id
- organization_id
- project_id
- document_asset_id (FK document_assets.id)
- status (`running|completed|partial|failed`)
- extractor_type
- ocr_used
- extracted_text
- extracted_tables_json
- column_detection_json
- confidence_score
- error_message
- started_at
- finished_at
- created_at/updated_at/created_by/updated_by

### document_classifications

- id
- organization_id
- project_id
- document_asset_id (FK document_assets.id)
- suggested_type
- confidence_score
- rationale_json
- status (`suggested|confirmed|rejected`)
- decided_by_user_id
- decided_at
- created_at/updated_at/created_by/updated_by

### document_structured_data

- id
- organization_id
- project_id
- document_asset_id (FK document_assets.id)
- schema_type
- payload_json
- payload_version
- status (`draft|pending_review|approved|rejected|superseded`)
- generated_by
- approved_by_user_id
- approved_at
- created_at/updated_at/created_by/updated_by

### document_links

- id
- organization_id
- project_id
- document_asset_id (FK document_assets.id)
- link_type (`sequence|scene|shot|take|report`)
- target_id
- confidence_score
- source (`manual|heuristic|ai`)
- is_primary
- created_at/updated_at/created_by/updated_by

## 3) Reportes estructurados

### camera_reports

- id
- organization_id
- project_id
- shooting_day_id (nullable)
- sequence_id (nullable)
- scene_id (nullable)
- shot_id (nullable)
- camera_label
- operator_name (nullable)
- card_or_mag
- take_reference (nullable)
- notes
- incidents
- report_date
- document_asset_id (nullable, FK document_assets.id)
- media_asset_id (nullable, FK media_assets.id)
- created_at/updated_at/created_by/updated_by

### sound_reports

- id
- organization_id
- project_id
- shooting_day_id (nullable)
- sequence_id (nullable)
- scene_id (nullable)
- shot_id (nullable)
- sound_roll
- mixer_name (nullable)
- boom_operator (nullable)
- sample_rate (nullable)
- bit_depth (nullable)
- timecode_notes (nullable)
- notes
- incidents
- report_date
- document_asset_id (nullable)
- media_asset_id (nullable)
- created_at/updated_at/created_by/updated_by

### script_notes

- id
- organization_id
- project_id
- shooting_day_id (nullable)
- sequence_id (nullable)
- scene_id (nullable)
- shot_id (nullable)
- best_take (nullable)
- continuity_notes
- editor_note (nullable)
- report_date
- document_asset_id (nullable)
- media_asset_id (nullable)
- created_at/updated_at/created_by/updated_by

### director_notes

- id
- organization_id
- project_id
- shooting_day_id (nullable)
- sequence_id (nullable)
- scene_id (nullable)
- shot_id (nullable)
- preferred_take (nullable)
- intention_note
- pacing_note (nullable)
- coverage_note (nullable)
- report_date
- document_asset_id (nullable)
- media_asset_id (nullable)
- created_at/updated_at/created_by/updated_by

## 4) Nota de implementacion

Este preview es la referencia de modelado para Sprint 9.
No implica que las tablas ya existan en codigo.

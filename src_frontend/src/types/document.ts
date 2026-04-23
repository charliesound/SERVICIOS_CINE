export interface DocumentExtraction {
  id: string
  document_asset_id: string
  extraction_status: string
  extraction_engine?: string | null
  raw_text?: string | null
  extracted_table_json?: Record<string, unknown> | null
  error_message?: string | null
  created_at: string
  updated_at: string
}

export interface DocumentClassification {
  id: string
  document_asset_id: string
  doc_type: string
  classification_status: string
  confidence_score?: number | null
  created_at: string
  updated_at: string
}

export interface DocumentStructuredData {
  id: string
  document_asset_id: string
  schema_type: string
  structured_payload_json: Record<string, unknown>
  review_status: string
  approved_by?: string | null
  approved_at?: string | null
  created_at: string
  updated_at: string
}

export interface DocumentLink {
  id: string
  document_asset_id: string
  organization_id: string
  project_id: string
  shooting_day_id?: string | null
  sequence_id?: string | null
  scene_id?: string | null
  shot_id?: string | null
  media_asset_id?: string | null
  created_at: string
}

export interface DocumentAsset {
  id: string
  organization_id: string
  project_id: string
  storage_source_id?: string | null
  media_asset_id?: string | null
  file_name: string
  file_extension: string
  mime_type?: string | null
  source_kind: string
  original_path?: string | null
  uploaded_by?: string | null
  status: string
  created_at: string
  extraction?: DocumentExtraction | null
  classification?: DocumentClassification | null
  structured_data?: DocumentStructuredData | null
  links: DocumentLink[]
}

export interface DocumentEvent {
  id: string
  organization_id: string
  project_id: string
  storage_source_id?: string | null
  document_asset_id?: string | null
  event_type: string
  event_payload_json?: Record<string, unknown> | null
  created_by?: string | null
  created_at: string
}

export interface DocumentAssetCreatePayload {
  organization_id?: string
  project_id?: string
  storage_source_id?: string
  media_asset_id?: string
  file_name?: string
  mime_type?: string
  source_kind?: string
  original_path?: string
  shooting_day_id?: string
  sequence_id?: string
  scene_id?: string
  shot_id?: string
}

export interface DocumentAssetUpdatePayload {
  status?: string
  original_path?: string
  structured_payload_json?: Record<string, unknown>
  review_status?: string
}

export interface DocumentApprovePayload {
  approved_by?: string
}

export interface DocumentListFilters {
  project_id?: string
  status?: string
  doc_type?: string
}

export interface DocumentAssetListResponse {
  documents: DocumentAsset[]
}

export interface DocumentEventListResponse {
  events: DocumentEvent[]
}

export interface DerivePreviewResponse {
  target_report_type: string
  initial_report_payload: Record<string, unknown>
  source_document_id: string
  allowed: boolean
  reason?: string | null
}

export interface DeriveReportRequest {
  report_payload: Record<string, unknown>
  report_type: string
  shooting_day_id?: string | null
  sequence_id?: string | null
  scene_id?: string | null
  shot_id?: string | null
  report_date?: string | null
}

export interface DeriveReportResponse {
  report_id: string
  report_type: string
  message: string
}

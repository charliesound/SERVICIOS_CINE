export type DocumentStatus =
  | 'registered'
  | 'extracted'
  | 'needs_review'
  | 'classified'
  | 'structured'
  | 'approved'
  | 'failed'

export type ExtractionStatus =
  | 'pending'
  | 'completed'
  | 'pending_ocr'
  | 'unsupported'
  | 'failed'

export type DocumentType =
  | 'camera_report'
  | 'sound_report'
  | 'script_note'
  | 'director_note'
  | 'operator_note'
  | 'unknown_document'

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
  status: DocumentStatus | string
  created_at: string
}

export interface DocumentAssetCreate {
  organization_id?: string
  project_id: string
  storage_source_id?: string | null
  media_asset_id?: string | null
  file_name?: string | null
  original_path?: string | null
  source_kind: string
}

export interface DocumentAssetUpdate {
  file_name?: string
  original_path?: string
  status?: string
}

export interface DocumentExtraction {
  id: string
  document_asset_id: string
  extraction_status: ExtractionStatus | string
  extraction_engine?: string | null
  raw_text?: string | null
  extracted_table_json?: unknown
  error_message?: string | null
  created_at: string
  updated_at: string
}

export interface DocumentClassification {
  id: string
  document_asset_id: string
  doc_type: DocumentType | string
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

export interface DocumentAssetDetail extends DocumentAsset {
  latest_extraction?: DocumentExtraction | null
  latest_classification?: DocumentClassification | null
  latest_structured_data?: DocumentStructuredData | null
}

export interface DocumentAssetListResponse {
  items: DocumentAsset[]
}

export interface IngestEventItem {
  id: string
  organization_id: string
  project_id: string
  storage_source_id?: string | null
  event_type: string
  event_payload_json: Record<string, unknown>
  created_by?: string | null
  created_at: string
}

export interface DocumentEventListResponse {
  items: IngestEventItem[]
}

export interface DocumentClassifyRequest {
  force?: boolean
}

export interface DocumentExtractRequest {
  force?: boolean
}

export interface DocumentStructureRequest {
  schema_type?: string | null
}

export interface DocumentApproveRequest {
  structured_payload_json?: Record<string, unknown>
}

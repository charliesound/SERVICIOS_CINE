export interface IngestScanLaunchPayload {
  watch_path_id?: string
}

export interface IngestScan {
  id: string
  organization_id: string
  project_id: string
  storage_source_id: string
  watch_path_id?: string | null
  status: string
  started_at: string
  finished_at?: string | null
  files_discovered_count: number
  files_indexed_count: number
  files_skipped_count: number
  error_message?: string | null
  created_by?: string | null
}

export interface MediaAsset {
  id: string
  organization_id: string
  project_id: string
  storage_source_id: string
  watch_path_id?: string | null
  ingest_scan_id?: string | null
  file_name: string
  relative_path: string
  canonical_path: string
  file_extension: string
  mime_type?: string | null
  asset_type: string
  file_size: number
  modified_at?: string | null
  discovered_at: string
  status: string
  created_by?: string | null
}

export interface IngestScanListResponse {
  scans: IngestScan[]
}

export interface MediaAssetListResponse {
  assets: MediaAsset[]
}

export interface IngestScanFilters {
  project_id?: string
  source_id?: string
  status?: string
}

export interface MediaAssetFilters {
  project_id?: string
  source_id?: string
  status?: string
  asset_type?: string
}

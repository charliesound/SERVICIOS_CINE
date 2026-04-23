export interface StorageSource {
  id: string
  organization_id: string
  project_id: string
  name: string
  source_type: string
  mount_path: string
  status: string
  created_by?: string | null
  created_at: string
  updated_at: string
}

export interface StorageAuthorization {
  id: string
  storage_source_id: string
  authorization_mode: string
  scope_path: string
  status: string
  granted_by?: string | null
  granted_at: string
  expires_at?: string | null
  revoked_at?: string | null
}

export interface StorageWatchPath {
  id: string
  storage_source_id: string
  watch_path: string
  status: string
  last_validated_at?: string | null
  created_at: string
}

export interface StoragePathMetadata {
  exists: boolean
  is_dir: boolean
  readable: boolean
  writable?: boolean
  free_space?: number | null
  total_space?: number | null
  normalized_path?: string
}

export interface StorageSourceCreatePayload {
  organization_id: string
  project_id: string
  name: string
  source_type: string
  mount_path: string
}

export interface StorageSourceUpdatePayload {
  name?: string
  status?: string
}

export interface StorageAuthorizationCreatePayload {
  authorization_mode: string
  scope_path: string
  expires_at?: string | null
}

export interface StorageWatchPathCreatePayload {
  watch_path: string
}

export interface StorageSourceListResponse {
  storage_sources: StorageSource[]
}

export interface StorageAuthorizationListResponse {
  authorizations: StorageAuthorization[]
}

export interface StorageWatchPathListResponse {
  watch_paths: StorageWatchPath[]
}

export interface StorageValidationResult {
  source_id: string
  mount_path: string
  metadata: StoragePathMetadata
}

export interface StorageHandshakeResult {
  source_id: string
  mount_path: string
  metadata: StoragePathMetadata
  validated: boolean
  authorizations: StorageAuthorization[]
}

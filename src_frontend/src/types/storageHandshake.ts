export type StorageSourceType = 'local_mounted_path' | 'smb_mounted_path' | 'nfs_mounted_path'
export type StorageSourceStatus = 'draft' | 'validated' | 'authorized' | 'error' | 'active'
export type WatchPathStatus = 'active' | 'invalid'

export interface StorageSource {
  id: string
  organization_id: string
  project_id: string
  name: string
  source_type: StorageSourceType | string
  mount_path: string
  status: StorageSourceStatus | string
  created_by: string
  created_at: string
  updated_at: string
}

export interface StorageSourceCreate {
  organization_id?: string
  project_id: string
  name: string
  source_type: StorageSourceType | string
  mount_path: string
}

export interface StorageSourceUpdate {
  name?: string
  source_type?: StorageSourceType | string
  mount_path?: string
  status?: string
}

export interface StorageSourceListResponse {
  items: StorageSource[]
}

export interface StorageValidateRequest {
  path_override?: string
}

export interface StorageHandshakeResult {
  source_id: string
  validated_path: string
  exists: boolean
  is_dir: boolean
  readable: boolean
  free_space?: number | null
  total_space?: number | null
  status: string
  message: string
}

export interface StorageAuthorizationCreate {
  authorization_mode: string
  scope_path: string
  expires_at?: string | null
}

export interface StorageAuthorization {
  id: string
  storage_source_id: string
  authorization_mode: string
  scope_path: string
  status: string
  granted_by: string
  granted_at: string
  expires_at?: string | null
  revoked_at?: string | null
}

export interface StorageWatchPathCreate {
  watch_path: string
}

export interface StorageWatchPath {
  id: string
  storage_source_id: string
  watch_path: string
  status: WatchPathStatus | string
  last_validated_at?: string | null
  created_at: string
}

export interface StorageWatchPathListResponse {
  items: StorageWatchPath[]
}

import api from './client'

export interface EditorialTake {
  id: string
  project_id: string
  organization_id: string
  scene_number?: number | null
  shot_number?: number | null
  take_number?: number | null
  camera_roll?: string | null
  sound_roll?: string | null
  camera_media_asset_id?: string | null
  sound_media_asset_id?: string | null
  video_filename?: string | null
  audio_filename?: string | null
  start_timecode?: string | null
  end_timecode?: string | null
  audio_timecode_start?: string | null
  audio_time_reference_samples?: number | null
  audio_sample_rate?: number | null
  audio_channels?: number | null
  audio_duration_seconds?: number | null
  audio_fps?: number | null
  audio_scene?: string | null
  audio_take?: string | null
  audio_circled?: boolean | null
  audio_metadata_status?: string | null
  audio_metadata?: Record<string, unknown> | null
  dual_system_status?: string | null
  sync_confidence?: number | null
  sync_method?: string | null
  sync_warning?: string | null
  duration_frames?: number | null
  fps?: number | null
  slate?: string | null
  script_status?: string | null
  director_status?: string | null
  camera_status?: string | null
  sound_status?: string | null
  reconciliation_status?: string | null
  is_circled: boolean
  is_best: boolean
  is_recommended: boolean
  score: number
  recommended_reason?: string | null
  conflict_flags: string[]
  notes?: string | null
  created_at: string
  updated_at: string
}

export interface EditorialRecommendedTake {
  scene_number?: number | null
  shot_number?: number | null
  take: EditorialTake
}

export interface AssemblyCutItem {
  id: string
  assembly_cut_id: string
  take_id?: string | null
  project_id: string
  scene_number?: number | null
  shot_number?: number | null
  take_number?: number | null
  source_media_asset_id?: string | null
  audio_media_asset_id?: string | null
  start_tc?: string | null
  end_tc?: string | null
  timeline_in?: number | null
  timeline_out?: number | null
  duration_frames?: number | null
  fps?: number | null
  recommended_reason?: string | null
  order_index: number
  created_at: string
}

export interface AssemblyCut {
  id: string
  project_id: string
  organization_id?: string | null
  name: string
  description?: string | null
  status?: string | null
  source_scope?: string | null
  source_version?: number | null
  metadata_json: Record<string, unknown>
  created_by?: string | null
  created_at?: string | null
  updated_at?: string | null
  items: AssemblyCutItem[]
}

export interface EditorialFCPXMLValidation {
  valid: boolean
  errors: string[]
  warnings: string[]
  clip_count: number
  asset_count: number
  fps?: number | null
}

export interface EditorialMediaRelinkEntry {
  clip_id: string
  clip_name: string
  role: string
  asset_id?: string | null
  filename: string
  resolved_path: string
  fcpxml_uri: string
  status: string
  reason: string
  duration_frames?: number | null
  start_timecode?: string | null
  scene?: number | string | null
  shot?: number | string | null
  take?: number | string | null
  video_asset_id?: string | null
  audio_asset_id?: string | null
  video_path?: string | null
  audio_path?: string | null
  video_status?: string | null
  audio_status?: string | null
  sync_method?: string | null
  sync_confidence?: number | null
  dual_system_status?: string | null
  take_warnings: string[]
  audio_metadata?: Record<string, unknown> | null
}

export interface EditorialAudioMetadata {
  status: string
  asset_id?: string | null
  filename: string
  sample_rate?: number | null
  channels?: number | null
  duration_seconds?: number | null
  bit_depth?: number | null
  codec?: string | null
  file_size?: number | null
  timecode?: string | null
  time_reference_samples?: number | null
  time_reference_seconds?: number | null
  fps?: number | null
  scene?: string | null
  shot?: string | null
  take?: string | null
  sound_roll?: string | null
  circled?: boolean | null
  notes?: string | null
  warnings: string[]
  raw_bext?: Record<string, unknown> | null
  raw_ixml?: Record<string, unknown> | null
  reason?: string | null
}

export interface EditorialMediaRelinkReport {
  generated_at: string
  project_id: string
  assembly_cut_id: string
  clip_count: number
  resolved_media_count: number
  offline_media_count: number
  missing_media_count: number
  warnings: string[]
  entries: EditorialMediaRelinkEntry[]
}

export interface EditorialFCPXMLStatus {
  deliverable_id?: string | null
  file_name: string
  file_path: string
  assembly_cut_id: string
  format_type: string
  clip_count: number
  route_status: Record<string, number>
  warnings: string[]
  validation: EditorialFCPXMLValidation
  media_relink_report: EditorialMediaRelinkReport
}

export interface DavinciPlatformExportRequest {
  platform: 'windows' | 'mac' | 'linux' | 'offline' | 'all'
  root_path?: string
  include_media?: boolean
  audio_mode?: 'conservative' | 'experimental'
}

export interface DavinciPlatformExportResponse {
  deliverable_id?: string | null
  file_name: string
  file_path?: string
  assembly_cut_id: string
  platform: string
  format_type: string
  root_path?: string | null
}

export const editorialApi = {
  listTakes: async (projectId: string): Promise<EditorialTake[]> => {
    const { data } = await api.get<{ takes: EditorialTake[] }>(`/projects/${projectId}/editorial/takes`)
    return data.takes
  },

  reconcile: async (projectId: string): Promise<Record<string, unknown>> => {
    const { data } = await api.post(`/projects/${projectId}/editorial/reconcile`)
    return data
  },

  score: async (projectId: string): Promise<Record<string, unknown>> => {
    const { data } = await api.post(`/projects/${projectId}/editorial/score`)
    return data
  },

  getAudioMetadata: async (projectId: string): Promise<EditorialAudioMetadata[]> => {
    const { data } = await api.get<{ project_id: string; audio_assets: EditorialAudioMetadata[] }>(`/projects/${projectId}/editorial/audio-metadata`)
    return data.audio_assets
  },

  scanAudioMetadata: async (projectId: string): Promise<{ project_id: string; audio_assets: EditorialAudioMetadata[] }> => {
    const { data } = await api.post<{ project_id: string; audio_assets: EditorialAudioMetadata[] }>(`/projects/${projectId}/editorial/audio-metadata/scan`)
    return data
  },

  listRecommendedTakes: async (projectId: string): Promise<EditorialRecommendedTake[]> => {
    const { data } = await api.get<{ recommended_takes: EditorialRecommendedTake[] }>(`/projects/${projectId}/editorial/recommended-takes`)
    return data.recommended_takes
  },

  generateAssembly: async (projectId: string): Promise<{ assembly_cut: AssemblyCut; items_created: number }> => {
    const { data } = await api.post<{ assembly_cut: AssemblyCut; items_created: number }>(`/projects/${projectId}/editorial/assembly`)
    return data
  },

  getAssembly: async (projectId: string): Promise<AssemblyCut> => {
    const { data } = await api.get<AssemblyCut>(`/projects/${projectId}/editorial/assembly`)
    return data
  },

  exportFCPXML: async (projectId: string): Promise<Blob> => {
    const { data } = await api.get(`/projects/${projectId}/editorial/export/fcpxml`, {
      responseType: 'blob',
    })
    return data
  },

  getFCPXMLStatus: async (projectId: string): Promise<EditorialFCPXMLStatus> => {
    const { data } = await api.get<EditorialFCPXMLStatus>(`/projects/${projectId}/editorial/export/fcpxml`, {
      params: { download: false },
    })
    return data
  },

  validateFCPXML: async (projectId: string): Promise<EditorialFCPXMLValidation> => {
    const { data } = await api.get<EditorialFCPXMLValidation>(`/projects/${projectId}/editorial/export/fcpxml/validate`)
    return data
  },

  getMediaRelinkReport: async (projectId: string): Promise<EditorialMediaRelinkReport> => {
    const { data } = await api.get<EditorialMediaRelinkReport>(`/projects/${projectId}/editorial/media-relink-report`)
    return data
  },

  exportEditorialPackage: async (projectId: string): Promise<Blob> => {
    const { data } = await api.post(`/projects/${projectId}/editorial/export/package`, undefined, {
      responseType: 'blob',
    })
    return data
  },

  exportDavinciPackage: async (projectId: string, payload: DavinciPlatformExportRequest): Promise<Blob> => {
    const { data } = await api.post(`/projects/${projectId}/editorial/export/davinci-package`, payload, {
      responseType: 'blob',
    })
    return data
  },
}

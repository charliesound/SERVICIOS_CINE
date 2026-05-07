export interface StoryboardShot {
  id: string
  project_id: string
  organization_id: string
  sequence_id?: string
  sequence_order: number
  scene_number?: number
  scene_heading?: string
  narrative_text?: string
  asset_id?: string
  shot_type?: string
  visual_mode?: string
  generation_mode?: string
  generation_job_id?: string
  version: number
  is_active: boolean
  asset_file_name?: string
  asset_mime_type?: string
  thumbnail_url?: string
  preview_url?: string
  created_at: string
  updated_at: string
}

export interface StoryboardShotListResponse {
  shots: StoryboardShot[]
}

export interface StoryboardShotCreate {
  sequence_id?: string
  sequence_order?: number
  narrative_text?: string
  asset_id?: string
  shot_type?: string
  visual_mode?: string
}

export interface StoryboardShotUpdate {
  sequence_id?: string
  sequence_order?: number
  narrative_text?: string
  asset_id?: string
  shot_type?: string
  visual_mode?: string
}

export interface StoryboardShotReorderItem {
  shot_id: string
  sequence_order: number
  sequence_id?: string
}

export interface StoryboardShotBulkReorderRequest {
  shots: StoryboardShotReorderItem[]
}

export interface ProjectImageAssetItem {
  asset_id: string
  file_name: string
  mime_type: string
  created_at: string
  preview_url: string
  thumbnail_url: string
}

export interface ProjectImageAssetPaginationMeta {
  page: number
  size: number
  total_items: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ProjectImageAssetsResponse {
  items: ProjectImageAssetItem[]
  meta: ProjectImageAssetPaginationMeta
}

export type StoryboardGenerationMode = 'FULL_SCRIPT' | 'SEQUENCE' | 'SCENE_RANGE' | 'SINGLE_SCENE' | 'SELECTED_SCENES'

export type StoryboardSelectionMode = StoryboardGenerationMode | 'SELECTED_SCENES'

export interface StoryboardSceneCandidate {
  scene_number: number
  scene_heading: string
  narrative_text?: string
  sequence_id?: string | null
  sequence_title?: string | null
  storyboard_status?: 'not_generated' | 'generated' | 'without_image' | 'pending'
  asset_id?: string | null
  thumbnail_url?: string | null
  preview_url?: string | null
  asset_file_name?: string | null
  selected?: boolean
  source?: 'analysis' | 'options' | 'parsed'
}

export interface StoryboardSequence {
  sequence_id: string
  sequence_number: number
  title: string
  summary: string
  included_scenes: number[]
  characters: string[]
  location?: string
  emotional_arc?: string
  estimated_duration?: number
  estimated_shots: number
  storyboard_status: string
  current_version: number
}

export interface StoryboardOptions {
  modes: StoryboardGenerationMode[]
  sequences: StoryboardSequence[]
  scenes_detected: Array<Record<string, unknown>>
  styles_available: string[]
  storyboard_status: Record<string, unknown>
}

export interface StoryboardGeneratePayload {
  mode: StoryboardSelectionMode
  generation_mode?: StoryboardSelectionMode
  sequence_id?: string | null
  sequence_ids?: string[]
  scene_start?: number | null
  scene_end?: number | null
  selected_scene_ids?: string[]
  scene_numbers?: number[] | string[]
  style_preset?: string
  visual_mode?: string
  shots_per_scene?: number
  max_scenes?: number | null
  overwrite?: boolean
}

export interface StoryboardGenerationJob {
  job_id: string
  status: string
  mode: StoryboardSelectionMode
  generation_mode?: StoryboardSelectionMode
  version: number
  sequence_id?: string | null
  sequence_ids?: string[]
  scene_start?: number | null
  scene_end?: number | null
  selected_scene_numbers?: number[]
  total_selected?: number
  total_scenes: number
  total_shots: number
  render_jobs?: Array<{ job_id: string; backend?: string; workflow_key?: string; storyboard_shot_id?: string }>
}

export interface StoryboardScopeResponse {
  project_id: string
  mode: StoryboardGenerationMode
  sequence_id?: string | null
  scene_number?: number | null
  version?: number | null
  shots: StoryboardShot[]
}

export interface StoryboardSequenceDetail {
  sequence: StoryboardSequence
  shots: StoryboardShot[]
}

export interface DirtyShot extends StoryboardShot {
  isDirty: boolean
}

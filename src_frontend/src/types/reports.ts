export type StructuredReportType = 'camera' | 'sound' | 'script' | 'director'

export interface BaseStructuredReport {
  id: string
  organization_id: string
  project_id: string
  shooting_day_id?: string | null
  sequence_id?: string | null
  scene_id?: string | null
  shot_id?: string | null
  report_date: string
  document_asset_id?: string | null
  media_asset_id?: string | null
  created_by?: string | null
  created_at: string
  updated_at: string
}

export interface CameraReport extends BaseStructuredReport {
  camera_label: string
  operator_name?: string | null
  card_or_mag: string
  take_reference?: string | null
  notes: string
  incidents: string
}

export interface SoundReport extends BaseStructuredReport {
  sound_roll: string
  mixer_name?: string | null
  boom_operator?: string | null
  sample_rate?: string | null
  bit_depth?: string | null
  timecode_notes?: string | null
  notes: string
  incidents: string
}

export interface ScriptNoteReport extends BaseStructuredReport {
  best_take?: string | null
  continuity_notes: string
  editor_note?: string | null
}

export interface DirectorNoteReport extends BaseStructuredReport {
  preferred_take?: string | null
  intention_note: string
  pacing_note?: string | null
  coverage_note?: string | null
}

export type StructuredReport = CameraReport | SoundReport | ScriptNoteReport | DirectorNoteReport

export interface StructuredReportPayload {
  organization_id?: string
  project_id?: string
  shooting_day_id?: string
  sequence_id?: string
  scene_id?: string
  shot_id?: string
  report_date?: string
  document_asset_id?: string
  media_asset_id?: string
  camera_label?: string
  operator_name?: string
  card_or_mag?: string
  take_reference?: string
  notes?: string
  incidents?: string
  sound_roll?: string
  mixer_name?: string
  boom_operator?: string
  sample_rate?: string
  bit_depth?: string
  timecode_notes?: string
  best_take?: string
  continuity_notes?: string
  editor_note?: string
  preferred_take?: string
  intention_note?: string
  pacing_note?: string
  coverage_note?: string
}

export interface CameraReportListResponse {
  reports: CameraReport[]
}

export interface SoundReportListResponse {
  reports: SoundReport[]
}

export interface ScriptNoteListResponse {
  reports: ScriptNoteReport[]
}

export interface DirectorNoteListResponse {
  reports: DirectorNoteReport[]
}

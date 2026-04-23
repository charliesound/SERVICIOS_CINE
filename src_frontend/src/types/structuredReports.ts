export type ReportType = 'camera' | 'sound' | 'script' | 'director'

interface BaseReport {
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

interface BaseReportPayload {
  organization_id?: string
  project_id: string
  shooting_day_id?: string | null
  sequence_id?: string | null
  scene_id?: string | null
  shot_id?: string | null
  report_date: string
  document_asset_id?: string | null
  media_asset_id?: string | null
}

export interface CameraReport extends BaseReport {
  camera_label: string
  operator_name?: string | null
  card_or_mag: string
  take_reference?: string | null
  notes: string
  incidents: string
}

export interface CameraReportCreate extends BaseReportPayload {
  camera_label: string
  operator_name?: string | null
  card_or_mag: string
  take_reference?: string | null
  notes: string
  incidents: string
}

export interface CameraReportUpdate {
  shooting_day_id?: string | null
  sequence_id?: string | null
  scene_id?: string | null
  shot_id?: string | null
  camera_label?: string
  operator_name?: string | null
  card_or_mag?: string
  take_reference?: string | null
  notes?: string
  incidents?: string
  report_date?: string
  document_asset_id?: string | null
  media_asset_id?: string | null
}

export interface SoundReport extends BaseReport {
  sound_roll: string
  mixer_name?: string | null
  boom_operator?: string | null
  sample_rate?: string | null
  bit_depth?: string | null
  timecode_notes?: string | null
  notes: string
  incidents: string
}

export interface SoundReportCreate extends BaseReportPayload {
  sound_roll: string
  mixer_name?: string | null
  boom_operator?: string | null
  sample_rate?: string | null
  bit_depth?: string | null
  timecode_notes?: string | null
  notes: string
  incidents: string
}

export interface SoundReportUpdate {
  shooting_day_id?: string | null
  sequence_id?: string | null
  scene_id?: string | null
  shot_id?: string | null
  sound_roll?: string
  mixer_name?: string | null
  boom_operator?: string | null
  sample_rate?: string | null
  bit_depth?: string | null
  timecode_notes?: string | null
  notes?: string
  incidents?: string
  report_date?: string
  document_asset_id?: string | null
  media_asset_id?: string | null
}

export interface ScriptNote extends BaseReport {
  best_take?: string | null
  continuity_notes: string
  editor_note?: string | null
}

export interface ScriptNoteCreate extends BaseReportPayload {
  best_take?: string | null
  continuity_notes: string
  editor_note?: string | null
}

export interface ScriptNoteUpdate {
  shooting_day_id?: string | null
  sequence_id?: string | null
  scene_id?: string | null
  shot_id?: string | null
  best_take?: string | null
  continuity_notes?: string
  editor_note?: string | null
  report_date?: string
  document_asset_id?: string | null
  media_asset_id?: string | null
}

export interface DirectorNote extends BaseReport {
  preferred_take?: string | null
  intention_note: string
  pacing_note?: string | null
  coverage_note?: string | null
}

export interface DirectorNoteCreate extends BaseReportPayload {
  preferred_take?: string | null
  intention_note: string
  pacing_note?: string | null
  coverage_note?: string | null
}

export interface DirectorNoteUpdate {
  shooting_day_id?: string | null
  sequence_id?: string | null
  scene_id?: string | null
  shot_id?: string | null
  preferred_take?: string | null
  intention_note?: string
  pacing_note?: string | null
  coverage_note?: string | null
  report_date?: string
  document_asset_id?: string | null
  media_asset_id?: string | null
}

export interface CameraReportListResponse {
  items: CameraReport[]
}

export interface SoundReportListResponse {
  items: SoundReport[]
}

export interface ScriptNoteListResponse {
  items: ScriptNote[]
}

export interface DirectorNoteListResponse {
  items: DirectorNote[]
}

export type StructuredReport = CameraReport | SoundReport | ScriptNote | DirectorNote
export type StructuredReportCreate = CameraReportCreate | SoundReportCreate | ScriptNoteCreate | DirectorNoteCreate
export type StructuredReportUpdate = CameraReportUpdate | SoundReportUpdate | ScriptNoteUpdate | DirectorNoteUpdate

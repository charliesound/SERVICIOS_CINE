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
  metadata_json?: Record<string, unknown> | null
  asset_file_name?: string
  asset_mime_type?: string
  thumbnail_url?: string
  preview_url?: string
  render_job_id?: string
  render_status?: string
  created_at: string
  updated_at: string
}

export interface CinematicShotMetadata {
  directorial_intent?: Record<string, unknown> | null
  montage_intent?: Record<string, unknown> | null
  editorial_beats?: Array<Record<string, unknown>>
  shot_editorial_purpose?: Record<string, unknown> | null
  prompt_spec?: Record<string, unknown> | null
  cinematic_intent_id?: string
  director_lens_id?: string
  validation?: Record<string, unknown> | null
  source_scope?: string
  sequence_id?: string | null
  sequence_title?: string | null
  sequence_summary?: string | null
  shot_plan_reason?: string
  script_excerpt_used?: string
  script_visual_alignment?: Record<string, unknown> | null
}

export interface ScriptSynopsisResult {
  logline: string
  synopsis_short: string
  synopsis_extended: string
  premise: string
  theme: string
  genre: string
  tone: string
  main_characters: string[]
  main_locations: string[]
  dramatic_structure: string
  production_notes: string[]
  recommended_storyboard_sequences: string[]
}

export interface ScriptSequenceMapEntry {
  sequence_id: string
  sequence_number: number
  title: string
  script_excerpt: string
  summary: string
  location: string
  time_of_day: string
  characters: string[]
  dramatic_function: string
  emotional_goal: string
  visual_opportunity: string
  production_complexity: string
  recommended_for_storyboard: boolean
  suggested_shot_count: number
  technical_notes: string[]
}

export interface ScriptSequenceMap {
  project_id: string
  script_id?: string | null
  sequences: ScriptSequenceMapEntry[]
  total_sequences: number
  recommended_priority_order: string[]
}

export interface FullScriptAnalysisResult {
  synopsis: ScriptSynopsisResult
  sequence_map: ScriptSequenceMap
  warnings: string[]
}

export interface PlannedStoryboardShot {
  shot_number: number
  shot_type: string
  framing: string
  camera_angle: string
  camera_movement: string
  lens_suggestion: string
  action: string
  characters: string[]
  location: string
  lighting: string
  emotional_intent: string
  continuity_notes: string[]
  prompt_brief: string
  negative_prompt_guidance: string
  shot_plan_reason: string
  script_excerpt_used: string
}

export interface SequenceStoryboardPlan {
  project_id: string
  sequence_id: string
  sequence_title: string
  sequence_summary: string
  shot_plan: PlannedStoryboardShot[]
  continuity_plan: string[]
  visual_style_guidance: string
  estimated_shot_count: number
  warnings: string[]
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
  director_lens_id?: string | null
  montage_profile_id?: string | null
  use_cinematic_intelligence?: boolean
  use_montage_intelligence?: boolean
  validate_prompts?: boolean
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

// --- Director Feedback Types ---

export type FeedbackCategory =
  | 'composition'
  | 'lighting'
  | 'character'
  | 'camera'
  | 'continuity'
  | 'tone'
  | 'production'
  | 'other'

export type FeedbackSeverity = 'minor' | 'medium' | 'major'

export interface DirectorFeedbackNote {
  note_id: string
  target_type: 'storyboard' | 'sequence' | 'shot' | 'prompt' | 'visual_reference'
  target_id: string
  note_text: string
  category: FeedbackCategory
  severity: FeedbackSeverity
  created_by_role: 'director' | 'producer' | 'cinematographer' | 'operator'
  preserve_original_logic: boolean
}

export interface DirectorFeedbackInterpretation {
  requested_changes: string[]
  protected_story_elements: string[]
  protected_visual_elements: string[]
  conflict_with_script: boolean
  conflict_with_script_details: string
  conflict_with_reference: boolean
  conflict_with_reference_details: string
  conflict_with_initial_prompt: boolean
  conflict_with_initial_prompt_details: string
  recommended_action: string
  risk_level: string
  explanation: string
}

export interface PromptRevisionPatch {
  original_prompt: string
  revised_prompt: string
  original_negative_prompt: string
  revised_negative_prompt: string
  preserved_elements: string[]
  changed_elements: string[]
  rejected_changes: string[]
  revision_reason: string
  director_note_applied: string
  version_number: number
}

export interface StoryboardRevisionPlan {
  project_id: string
  sequence_id: string
  shot_id?: string | null
  original_story_logic: string
  director_feedback?: DirectorFeedbackNote | null
  interpretation?: DirectorFeedbackInterpretation | null
  prompt_revision?: PromptRevisionPatch | null
  regeneration_strategy: 'single_shot' | 'selected_shots' | 'sequence' | 'full_storyboard_not_allowed'
  requires_director_confirmation: boolean
  qa_checklist: string[]
}

export interface StoryboardRevisionResult {
  status: string
  revision_id: string
  revision_plan: StoryboardRevisionPlan
  revised_prompt_spec: Record<string, unknown>
  metadata_json: Record<string, unknown>
  message: string
}

export interface ShotFeedbackRequest {
  note_text: string
  category: FeedbackCategory
  severity: FeedbackSeverity
  created_by_role: 'director' | 'producer' | 'cinematographer' | 'operator'
  preserve_original_logic: boolean
}

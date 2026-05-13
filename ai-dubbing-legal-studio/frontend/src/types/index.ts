export interface User {
  id: number
  email: string
  name: string
  role: string
  is_active: boolean
  organization_id: number | null
  created_at: string
}

export interface Project {
  id: number
  name: string
  description?: string
  organization_id: number
  created_by: number
  status: string
  created_at: string
  updated_at?: string
}

export interface Actor {
  id: number
  name: string
  email?: string
  voice_gender?: string
  voice_language?: string
  notes?: string
  is_active: boolean
  created_at: string
}

export interface VoiceContract {
  id: number
  actor_id: number
  organization_id: number
  contract_ref: string
  signed_date: string
  expiry_date: string
  is_active: boolean
  ia_consent: boolean
  allowed_languages: string
  allowed_territories: string
  allowed_usage_types: string
  max_duration_seconds?: number
  compensation_terms?: string
  document_path?: string
  notes?: string
  created_at: string
  updated_at?: string
}

export type DubbingMode = 'doblaje_humano_asistido' | 'voz_original_ia_autorizada'

export type JobStatus =
  | 'uploaded'
  | 'pending_legal_check'
  | 'blocked_legal'
  | 'transcribing'
  | 'translating'
  | 'awaiting_translation_review'
  | 'generating_voice'
  | 'lipsyncing'
  | 'mixing'
  | 'awaiting_approval'
  | 'approved'
  | 'rejected'
  | 'exported'
  | 'failed'

export interface DubbingJob {
  id: number
  project_id: number
  media_asset_id?: number
  actor_id?: number
  contract_id?: number
  status: JobStatus
  mode: DubbingMode
  source_language: string
  target_language: string
  territory?: string
  usage_type?: string
  legal_blocked: boolean
  legal_block_reason?: string
  tts_provider_used?: string
  lipsync_provider_used?: string
  model_version?: string
  output_path?: string
  created_by: number
  created_at: string
  updated_at?: string
}

export interface AuditLog {
  id: number
  user_id?: number
  organization_id?: number
  project_id?: number
  dubbing_job_id?: number
  action: string
  entity_type?: string
  entity_id?: number
  details?: string
  ip_address?: string
  created_at: string
}

export interface ContractValidationResult {
  contract_id: number
  blocked: boolean
  reason?: string
  checks: Record<string, boolean>
}

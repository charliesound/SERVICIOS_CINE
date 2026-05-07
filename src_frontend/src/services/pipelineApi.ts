import api from '@/api/client'

export type PipelineMode = 'storyboard' | 'image' | 'video' | 'dubbing' | 'sound' | 'editorial' | 'pitch'

export interface PipelineValidationIssue {
  code: string
  message: string
  severity: string
  field?: string | null
}

export interface PipelineValidationResponse {
  valid: boolean
  blocked: boolean
  errors: PipelineValidationIssue[]
  warnings: PipelineValidationIssue[]
}

export interface PipelineLegalContext {
  voice_cloning: boolean
  consent: boolean
  rights_declared: boolean
  rights_notes?: string | null
}

export interface PipelineStage {
  id: string
  name: string
  type: string
  inputs: string[]
  outputs: string[]
  config: Record<string, unknown>
}

export interface PipelineDefinition {
  pipeline_id: string
  mode: string
  title: string
  summary?: string | null
  preset_key: string
  preset_name: string
  task_type: string
  project_id?: string | null
  intent?: string | null
  workflow_key?: string | null
  backend?: string | null
  stages: PipelineStage[]
  legal: PipelineLegalContext
  metadata: Record<string, unknown>
}

export interface PipelinePreset {
  key: string
  name: string
  description: string
  task_type: string
  mode: string
  requires_legal_gate: boolean
  default_workflow_key?: string | null
  default_backend?: string | null
  stage_count: number
}

export interface PipelinePresetListResponse {
  count: number
  presets: PipelinePreset[]
}

export interface PipelineGeneratePayload {
  intent?: string
  preset_key?: string
  title?: string
  project_id?: string
  context?: Record<string, unknown>
  legal?: PipelineLegalContext
}

export interface PipelineGenerateResponse {
  mode: string
  pipeline: PipelineDefinition
  validation: PipelineValidationResponse
}

export interface PipelineValidatePayload {
  pipeline: PipelineDefinition
  project_id?: string
}

export interface PipelineJobHistoryEvent {
  id: string
  event_type: string
  status: string
  message: string
  created_at: string
}

export interface PipelineJob {
  job_id: string
  mode: string
  status: string
  organization_id: string
  user_id: string
  project_id?: string | null
  pipeline_id: string
  task_type: string
  preset_key: string
  created_at: string
  updated_at: string
  validation: PipelineValidationResponse
  history: PipelineJobHistoryEvent[]
  pipeline: PipelineDefinition
}

export interface PipelineExecutePayload {
  pipeline: PipelineDefinition
  project_id?: string
}

export interface PipelineExecuteResponse {
  mode: string
  job: PipelineJob
}

export interface PipelineJobListResponse {
  count: number
  jobs: PipelineJob[]
}

export const pipelineModeToPreset: Record<PipelineMode, string> = {
  storyboard: 'storyboard_from_script',
  image: 'storyboard_from_script',
  video: 'teaser_from_script',
  dubbing: 'ai_dubbing_with_legal_gate',
  sound: 'sound_cleanup',
  editorial: 'teaser_from_script',
  pitch: 'audiovisual_pitch_deck',
}

export const pipelineApi = {
  listPresets: async (): Promise<PipelinePresetListResponse> => {
    const { data } = await api.get<PipelinePresetListResponse>('/workflows/presets')
    return data
  },

  generate: async (payload: PipelineGeneratePayload): Promise<PipelineGenerateResponse> => {
    const { data } = await api.post<PipelineGenerateResponse>('/workflows/plan', payload)
    return data
  },

  validate: async (payload: PipelineValidatePayload): Promise<PipelineValidationResponse> => {
    const { data } = await api.post<PipelineValidationResponse>('/workflows/validate', payload)
    return data
  },

  execute: async (payload: PipelineExecutePayload): Promise<PipelineExecuteResponse> => {
    const { data } = await api.post<PipelineExecuteResponse>('/workflows/build', payload)
    return data
  },

  listJobs: async (projectId?: string): Promise<PipelineJobListResponse> => {
    const { data } = await api.get<PipelineJobListResponse>('/pipelines/jobs', {
      params: projectId ? { project_id: projectId } : undefined,
    })
    return data
  },
}

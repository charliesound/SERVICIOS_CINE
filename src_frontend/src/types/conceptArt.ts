export interface ConceptArtDryRunPayload {
  prompt: string
  negative_prompt?: string
  width?: number
  height?: number
  steps?: number
  cfg?: number
  seed?: number
}

export interface ConceptArtPipeline {
  task_type: string
  workflow_id: string
  model_family: string
  workflow_status: string
  unet: string | null
  clip_l: string | null
  t5xxl: string | null
  vae: string | null
  checkpoint: string | null
  missing_models: string[]
  params: {
    width: number
    height: number
    steps: number
    cfg: number
    sampler: string
    scheduler: string
  }
  safe_to_render: boolean
  reason: string
  alternatives: string[]
}

export interface CompiledWorkflowValidation {
  valid: boolean
  missing_placeholders: string[]
  node_count: number
  model_family: string
}

export interface CompiledWorkflowPreview {
  status: string
  workflow_id: string
  template_path: string
  model_family: string
  ready_for_comfyui_prompt: boolean
  requires_template_mapping: boolean
  template_mapping_status: string
  compiled_workflow: Record<string, unknown>
  validation: CompiledWorkflowValidation
}

export interface ConceptArtDryRunResponse {
  status: string
  project_id: string
  job_id: string
  workflow_id: string
  pipeline: ConceptArtPipeline
  compiled_workflow_preview: CompiledWorkflowPreview
  dry_run: boolean
  render_executed: boolean
  prompt_called: boolean
}

export interface ConceptArtJobSummary {
  job_id: string
  task_type: string
  status: string
  workflow_id: string | null
  model_family: string | null
  safe_to_render: boolean
  dry_run: boolean
  render_executed: boolean
  prompt_called: boolean
  created_at: string | null
  created_by: string | null
}

export interface ConceptArtJobsResponse {
  status: string
  project_id: string
  jobs: ConceptArtJobSummary[]
}

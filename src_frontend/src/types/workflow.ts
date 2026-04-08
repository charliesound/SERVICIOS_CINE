export type WorkflowCategory = 'still' | 'video' | 'dubbing' | 'lab'

export interface WorkflowCatalogItem {
  key: string
  name: string
  category: WorkflowCategory
  backend: string
  description: string
  required_inputs: string[]
  optional_inputs: string[]
  tags: string[]
}

export interface IntentAnalysis {
  task_type: string
  backend: string
  detected_workflow: string
  confidence: number
  reasoning: string
  missing_inputs: string[]
  suggested_params: Record<string, any>
  workflow?: Record<string, any>
}

export interface WorkflowPlanRequest {
  intent: string
  context: Record<string, any>
}

export interface Preset {
  id: string
  name: string
  workflow_key: string
  description: string
  category: string
  backend: string
  tags: string[]
  is_public: boolean
  created_by: string
  created_at: string
}

export interface PresetCreate {
  name: string
  workflow_key: string
  inputs: Record<string, any>
  description?: string
  tags?: string[]
  is_public?: boolean
}

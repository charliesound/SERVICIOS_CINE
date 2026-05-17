export type ScriptAnalysisExportFormat = 'json' | 'md'

export type ScriptAnalysisStatus =
  | 'none'
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed'

export interface ScriptAnalysisSummary {
  status?: string
  scenes_count?: number
  characters_count?: number
  locations_count?: number
  sequences_count?: number
  summary?: Record<string, unknown>
  scenes?: Array<Record<string, unknown>>
  source?: 'breakdown' | 'document'
}

export interface ScriptAnalysisExportPayload {
  export_version: string
  source: string
  project_id: string
  project_name: string
  generated_at: string
  has_analysis: boolean
  has_script: boolean
  warnings: string[]
  logline?: string
  synopsis_short?: string
  synopsis_extended?: string
  premise?: string
  theme?: string
  genre?: string
  tone?: string
  dramatic_structure?: string
  characters?: string[]
  locations?: string[]
  scenes?: Array<Record<string, unknown>>
  sequences?: Array<Record<string, unknown>>
  breakdowns?: Array<Record<string, unknown>>
  department_breakdown?: Record<string, unknown>
  analysis_engine?: string
  analysis_summary?: Record<string, unknown>
  production_notes?: string[]
  storyboard_suggestions?: string[]
  analysis_created_at?: string | null
  analysis_updated_at?: string | null
}

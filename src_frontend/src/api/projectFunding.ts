import api from './client'

export interface ProjectFundingSource {
  id: string
  project_id: string
  organization_id: string
  source_name: string
  source_type: string
  amount: number
  currency: string
  status: string
  notes: string | null
  created_at: string | null
  updated_at: string | null
}

export interface ProjectFundingSummary {
  total_budget: number
  total_secured_private_funds: number
  total_negotiating_private_funds: number
  total_projected_private_funds: number
  current_funding_gap: number
  optimistic_funding_gap: number
  currency: string
}

export interface CreateFundingSourcePayload {
  source_name: string
  source_type: string
  amount: number
  currency?: string
  status?: string
  notes?: string
}

export interface UpdateFundingSourcePayload {
  source_name?: string
  source_type?: string
  amount?: number
  currency?: string
  status?: string
  notes?: string
}

export type FundingFitLevel = 'high' | 'medium' | 'low' | 'blocked'
export type FundingRegionScope = 'spain' | 'europe' | 'iberoamerica_latam'
export type FundingSortBy = 'match_score' | 'deadline' | 'fit_level'
export type FundingSortDir = 'asc' | 'desc'

export interface FundingMatchListParams {
  page?: number
  size?: number
  sort_by?: FundingSortBy
  sort_dir?: FundingSortDir
  fit_level?: FundingFitLevel | ''
  region_scope?: FundingRegionScope | ''
  q?: string
}

export interface FundingProfile {
  project_id: string
  organization_id: string
  title: string
  type_of_work: string
  phase: string
  logline: string
  synopsis: string
  language: string
  countries_involved: string[]
  budget_total: number
  funding_gap: number
  funding_gap_band: string
  has_breakdown: boolean
  has_budget: boolean
  has_synopsis: boolean
}

export interface FundingChecklist {
  project_id: string
  total_opportunities: number
  high_matches: number
  medium_matches: number
  low_matches: number
  blocked_matches: number
  documents: string[]
  blockers: string[]
  priority_actions: string[]
  deadline_risks: Array<{
    funding_call_id: string
    title: string
    deadline_at: string
    fit_level: FundingFitLevel
  }>
}

export interface FundingRequirementEvaluation {
  requirement: string
  status: 'met' | 'partially_met' | 'unmet' | 'unknown'
  evidence_excerpt: string
  reasoning: string
  confidence: 'high' | 'medium' | 'low'
  category?: string | null
  is_mandatory: boolean
  supporting_chunk_id?: string | null
}

export interface FundingEvidenceChunk {
  chunk_id: string
  document_id: string
  file_name: string
  document_type: string
  chunk_index: number
  score: number
  chunk_text: string
  metadata_json?: Record<string, unknown> | null
  queries?: string[]
}

export interface FundingMatch {
  match_id: string
  funding_call_id: string
  source_id: string
  source_code: string
  source_name: string
  source_region: FundingRegionScope | string
  region_scope: FundingRegionScope | string
  title: string
  status: string
  opportunity_type: string | null
  phase: string | null
  deadline_at: string | null
  official_url: string | null
  match_score: number
  baseline_score: number | null
  rag_enriched_score: number | null
  fit_level: FundingFitLevel
  fit_summary: string
  blocking_reasons_json: string[]
  missing_documents_json: string[]
  recommended_actions_json: string[]
  confidence_level: string | null
  rag_confidence_level: string | null
  rag_rationale: string | null
  rag_missing_requirements: string[]
  matcher_mode: string
  evaluation_version: string | null
  computed_at: string | null
  evidence_chunks_json: {
    queries?: string[]
    retrieved_chunks?: FundingEvidenceChunk[]
    requirement_evaluations?: FundingRequirementEvaluation[]
    document_inventory?: Array<{
      document_id: string
      document_type: string
      file_name: string
    }>
  }
}

export interface FundingMatchesResponse {
  project_id: string
  count: number
  total: number
  page: number | null
  size: number | null
  pages: number
  sort_by: FundingSortBy
  sort_dir: FundingSortDir
  filters: {
    fit_level: string | null
    region_scope: string | null
    q: string | null
  }
  matches: FundingMatch[]
  job?: {
    job_id: string
    status: string
    error_message: string | null
    completed_at: string | null
  } | null
}

export interface FundingMatchEvidence extends FundingMatch {
  project_id: string
  organization_id: string
}

export interface FundingMatcherStatus {
  project_id: string
  organization_id: string
  matcher_mode: string
  has_results: boolean
  matches_count: number
  job: {
    job_id: string
    status: string
    error_message: string | null
    created_at: string | null
    completed_at: string | null
    result_data: Record<string, unknown> | null
  } | null
}

export interface FundingRecomputeResponse {
  job_id: string
  project_id: string
  organization_id: string
  status: string
  matcher_mode: string
  evaluation_version: string
}

function buildFundingMatchParams(params?: FundingMatchListParams) {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.size) searchParams.set('size', String(params.size))
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by)
  if (params?.sort_dir) searchParams.set('sort_dir', params.sort_dir)
  if (params?.fit_level) searchParams.set('fit_level', params.fit_level)
  if (params?.region_scope) searchParams.set('region_scope', params.region_scope)
  if (params?.q?.trim()) searchParams.set('q', params.q.trim())
  return searchParams
}

export const projectFundingApi = {
  listSources: async (projectId: string): Promise<ProjectFundingSource[]> => {
    const { data } = await api.get<{ project_id: string; count: number; sources: ProjectFundingSource[] }>(
      `/projects/${projectId}/funding/private-sources`
    )
    return data.sources
  },

  createSource: async (
    projectId: string,
    payload: CreateFundingSourcePayload
  ): Promise<{ project_id: string; source: ProjectFundingSource }> => {
    const { data } = await api.post<{ project_id: string; source: ProjectFundingSource }>(
      `/projects/${projectId}/funding/private-sources`,
      payload
    )
    return data
  },

  updateSource: async (
    projectId: string,
    sourceId: string,
    payload: UpdateFundingSourcePayload
  ): Promise<{ project_id: string; source: ProjectFundingSource }> => {
    const { data } = await api.patch<{ project_id: string; source: ProjectFundingSource }>(
      `/projects/${projectId}/funding/private-sources/${sourceId}`,
      payload
    )
    return data
  },

  deleteSource: async (projectId: string, sourceId: string): Promise<{ project_id: string; status: string }> => {
    const { data } = await api.delete<{ project_id: string; status: string }>(
      `/projects/${projectId}/funding/private-sources/${sourceId}`
    )
    return data
  },

  getSummary: async (projectId: string): Promise<ProjectFundingSummary> => {
    const { data } = await api.get<{ project_id: string } & ProjectFundingSummary>(
      `/projects/${projectId}/funding/private-summary`
    )
    return data
  },

  getProfile: async (projectId: string): Promise<FundingProfile> => {
    const { data } = await api.get<FundingProfile>(`/projects/${projectId}/funding/profile`)
    return data
  },

  getChecklist: async (projectId: string): Promise<FundingChecklist> => {
    const { data } = await api.get<FundingChecklist>(`/projects/${projectId}/funding/checklist`)
    return data
  },

  getMatches: async (projectId: string, params?: FundingMatchListParams): Promise<FundingMatchesResponse> => {
    const query = buildFundingMatchParams(params).toString()
    const { data } = await api.get<FundingMatchesResponse>(
      `/projects/${projectId}/funding/matches${query ? `?${query}` : ''}`
    )
    return data
  },

  getRagMatches: async (projectId: string, params?: FundingMatchListParams): Promise<FundingMatchesResponse> => {
    const query = buildFundingMatchParams(params).toString()
    const { data } = await api.get<FundingMatchesResponse>(
      `/projects/${projectId}/funding/matches-rag${query ? `?${query}` : ''}`
    )
    return data
  },

  getMatchEvidence: async (projectId: string, matchId: string): Promise<FundingMatchEvidence> => {
    const { data } = await api.get<FundingMatchEvidence>(`/projects/${projectId}/funding/matches/${matchId}/evidence`)
    return data
  },

  getMatcherStatus: async (projectId: string): Promise<FundingMatcherStatus> => {
    const { data } = await api.get<FundingMatcherStatus>(`/projects/${projectId}/funding/matcher-status`)
    return data
  },

  recomputeRag: async (projectId: string): Promise<FundingRecomputeResponse> => {
    const { data } = await api.post<FundingRecomputeResponse>(`/projects/${projectId}/funding/recompute-rag`)
    return data
  },
}

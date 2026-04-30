import api from './client'

export interface DistributionPack {
  id: string
  project_id: string
  title: string
  pack_type: string
  status: string
  logline: string | null
  short_synopsis: string | null
  commercial_positioning: string | null
  target_audience: string | null
  comparables: Array<{ title: string; year: number; box_office: string }>
  release_strategy: Record<string, unknown>
  exploitation_windows: Array<{ territory: string; window: string; timing: string }>
  territory_strategy: Array<{ priority: string; territory: string }>
  marketing_hooks: string[]
  available_materials: Array<{ material: string; status: string }>
  technical_specs: Record<string, unknown>
  sales_arguments: string[]
  risks: string[]
}

export interface GenerateDistributionPayload {
  pack_type: string
}

export const distributionPackApi = {
  list: async (projectId: string): Promise<{ packs: Array<{ id: string; title: string; pack_type: string; status: string }> }> => {
    const { data } = await api.get<{ packs: Array<{ id: string; title: string; pack_type: string; status: string }> }>(
      `/projects/${projectId}/distribution-packs`
    )
    return data
  },

  generate: async (projectId: string, payload: GenerateDistributionPayload): Promise<{ pack_id: string; status: string; pack_type: string }> => {
    const { data } = await api.post<{ pack_id: string; status: string; pack_type: string }>(
      `/projects/${projectId}/distribution-packs/generate`,
      payload
    )
    return data
  },

  get: async (projectId: string, packId: string): Promise<{ pack: DistributionPack }> => {
    const { data } = await api.get<{ pack: DistributionPack }>(
      `/projects/${projectId}/distribution-packs/${packId}`
    )
    return data
  },

  update: async (projectId: string, packId: string, payload: Partial<DistributionPack>): Promise<{ pack_id: string; status: string }> => {
    const { data } = await api.patch<{ pack_id: string; status: string }>(
      `/projects/${projectId}/distribution-packs/${packId}`,
      payload
    )
    return data
  },

  approve: async (projectId: string, packId: string): Promise<{ pack_id: string; status: string }> => {
    const { data } = await api.post<{ pack_id: string; status: string }>(
      `/projects/${projectId}/distribution-packs/${packId}/approve`,
      {}
    )
    return data
  },

  archive: async (projectId: string, packId: string): Promise<{ pack_id: string; status: string }> => {
    const { data } = await api.post<{ pack_id: string; status: string }>(
      `/projects/${projectId}/distribution-packs/${packId}/archive`,
      {}
    )
    return data
  },

  exportJson: async (projectId: string, packId: string): Promise<Record<string, unknown>> => {
    const { data } = await api.get<Record<string, unknown>>(
      `/projects/${projectId}/distribution-packs/${packId}/export/json`
    )
    return data
  },

  exportMarkdown: async (projectId: string, packId: string): Promise<string> => {
    const { data } = await api.get<string>(
      `/projects/${projectId}/distribution-packs/${packId}/export/markdown`
    )
    return data
  },

  exportZip: async (projectId: string, packId: string): Promise<Blob> => {
    const response = await api.get<string>(
      `/projects/${projectId}/distribution-packs/${packId}/export/zip`,
      { responseType: 'blob' as const }
    )
    return response.data as unknown as Blob
  },
}

export interface SalesTarget {
  id: string
  name: string
  target_type: string
  country: string | null
  region: string | null
  source_type: string
}

export interface SalesOpportunity {
  id: string
  target_type: string
  status: string
  fit_score: number
  fit_summary: string | null
  next_action: string | null
}

export const salesTargetsApi = {
  list: async (targetType?: string, status?: string): Promise<{ targets: SalesTarget[] }> => {
    const params = new URLSearchParams()
    if (targetType) params.set('target_type', targetType)
    if (status) params.set('status', status)
    const { data } = await api.get<{ targets: SalesTarget[] }>(
      `/sales-targets?${params.toString()}`
    )
    return data
  },

  create: async (payload: Partial<SalesTarget>): Promise<{ target_id: string }> => {
    const { data } = await api.post<{ target_id: string }>(
      '/sales-targets',
      payload
    )
    return data
  },

  suggest: async (projectId: string, targetType?: string): Promise<{ suggested_targets: SalesTarget[] }> => {
    const params = new URLSearchParams()
    if (targetType) params.set('target_type', targetType)
    const { data } = await api.get<{ suggested_targets: SalesTarget[] }>(
      `/projects/${projectId}/sales-opportunities/suggest?${params.toString()}`
    )
    return data
  },

  listOpportunities: async (projectId: string): Promise<{ opportunities: SalesOpportunity[] }> => {
    const { data } = await api.get<{ opportunities: SalesOpportunity[] }>(
      `/projects/${projectId}/sales-opportunities`
    )
    return data
  },

  createOpportunity: async (projectId: string, payload: Partial<SalesOpportunity>): Promise<{ opportunity_id: string; status: string }> => {
    const { data } = await api.post<{ opportunity_id: string; status: string }>(
      `/projects/${projectId}/sales-opportunities`,
      payload
    )
    return data
  },

  updateOpportunity: async (projectId: string, opportunityId: string, payload: Partial<SalesOpportunity>): Promise<{ opportunity_id: string; status: string }> => {
    const { data } = await api.patch<{ opportunity_id: string; status: string }>(
      `/projects/${projectId}/sales-opportunities/${opportunityId}`,
      payload
    )
    return data
  },
}
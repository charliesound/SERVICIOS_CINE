import api from './client'

export interface ProducerPitchPack {
  id: string
  project_id: string
  title: string
  status: string
  logline: string | null
  short_synopsis: string | null
  long_synopsis: string | null
  intention_note: string | null
  genre: string | null
  format: string | null
  tone: string | null
  target_audience: string | null
  commercial_strengths: string[]
  production_needs: string[]
  budget_summary: Record<string, unknown>
  funding_summary: Record<string, unknown>
  storyboard_selection: Array<{
    shot_number: number
    description: string
    camera_angle: string
    shot_type: string
  }>
  risks: string[]
}

export interface PitchPackUpdate {
  title?: string
  logline?: string
  short_synopsis?: string
  long_synopsis?: string
  intention_note?: string
  genre?: string
  format?: string
  tone?: string
  target_audience?: string
}

export const producerPitchApi = {
  list: async (projectId: string): Promise<{ packs: Array<{ id: string; title: string; status: string; logline: string | null; created_at: string }> }> => {
    const { data } = await api.get<{ packs: Array<{ id: string; title: string; status: string; logline: string | null; created_at: string }> }>(
      `/projects/${projectId}/producer-pitch`
    )
    return data
  },

  getActive: async (projectId: string): Promise<{ pack: ProducerPitchPack }> => {
    const { data } = await api.get<{ pack: ProducerPitchPack }>(
      `/projects/${projectId}/producer-pitch/active`
    )
    return data
  },

  generate: async (projectId: string): Promise<{ pack_id: string; status: string }> => {
    const { data } = await api.post<{ pack_id: string; status: string }>(
      `/projects/${projectId}/producer-pitch/generate`,
      {}
    )
    return data
  },

  get: async (projectId: string, packId: string): Promise<{ pack: ProducerPitchPack }> => {
    const { data } = await api.get<{ pack: ProducerPitchPack }>(
      `/projects/${projectId}/producer-pitch/${packId}`
    )
    return data
  },

  update: async (projectId: string, packId: string, payload: PitchPackUpdate): Promise<{ pack_id: string; status: string }> => {
    const { data } = await api.patch<{ pack_id: string; status: string }>(
      `/projects/${projectId}/producer-pitch/${packId}`,
      payload
    )
    return data
  },

  approve: async (projectId: string, packId: string): Promise<{ pack_id: string; status: string }> => {
    const { data } = await api.post<{ pack_id: string; status: string }>(
      `/projects/${projectId}/producer-pitch/${packId}/approve`,
      {}
    )
    return data
  },

  archive: async (projectId: string, packId: string): Promise<{ pack_id: string; status: string }> => {
    const { data } = await api.post<{ pack_id: string; status: string }>(
      `/projects/${projectId}/producer-pitch/${packId}/archive`,
      {}
    )
    return data
  },

  exportJson: async (projectId: string, packId: string): Promise<Record<string, unknown>> => {
    const { data } = await api.get<Record<string, unknown>>(
      `/projects/${projectId}/producer-pitch/${packId}/export/json`
    )
    return data
  },

  exportMarkdown: async (projectId: string, packId: string): Promise<string> => {
    const { data } = await api.get<string>(
      `/projects/${projectId}/producer-pitch/${packId}/export/markdown`
    )
    return data
  },

  exportZip: async (projectId: string, packId: string): Promise<Blob> => {
    const response = await api.get<string>(
      `/projects/${projectId}/producer-pitch/${packId}/export/zip`,
      { responseType: 'blob' as const }
    )
    return response.data as unknown as Blob
  },
}
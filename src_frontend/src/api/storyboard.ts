import api from './client'
import type {
  StoryboardShot,
  StoryboardShotListResponse,
  StoryboardShotCreate,
  StoryboardShotUpdate,
  StoryboardShotBulkReorderRequest,
  ProjectImageAssetsResponse,
  StoryboardGeneratePayload,
  StoryboardGenerationJob,
  StoryboardOptions,
  StoryboardScopeResponse,
  StoryboardSequence,
  StoryboardSequenceDetail,
} from '@/types/storyboard'

export const storyboardApi = {
  listShots: async (projectId: string): Promise<StoryboardShot[]> => {
    const { data } = await api.get<StoryboardShotListResponse>(`/projects/${projectId}/shots`)
    return data.shots
  },

  createShot: async (projectId: string, payload: StoryboardShotCreate): Promise<StoryboardShot> => {
    const { data } = await api.post<StoryboardShot>(`/projects/${projectId}/shots`, payload)
    return data
  },

  updateShot: async (projectId: string, shotId: string, payload: StoryboardShotUpdate): Promise<StoryboardShot> => {
    const { data } = await api.put<StoryboardShot>(`/projects/${projectId}/shots/${shotId}`, payload)
    return data
  },

  deleteShot: async (projectId: string, shotId: string): Promise<void> => {
    await api.delete(`/projects/${projectId}/shots/${shotId}`)
  },

  bulkReorder: async (projectId: string, payload: StoryboardShotBulkReorderRequest): Promise<StoryboardShot[]> => {
    const { data } = await api.put<StoryboardShotListResponse>(`/projects/${projectId}/shots/bulk-reorder`, payload)
    return data.shots
  },

  getImageAssets: async (projectId: string, page = 1, size = 20): Promise<ProjectImageAssetsResponse> => {
    const { data } = await api.get<ProjectImageAssetsResponse>(
      `/projects/${projectId}/assets/image-assets`,
      { params: { page, size } }
    )
    return data
  },

  getOptions: async (projectId: string): Promise<StoryboardOptions> => {
    const { data } = await api.get<StoryboardOptions>(`/projects/${projectId}/storyboard/options`)
    return data
  },

  listSequences: async (projectId: string): Promise<StoryboardSequence[]> => {
    const { data } = await api.get<StoryboardSequence[]>(`/projects/${projectId}/storyboard/sequences`)
    return data
  },

  generate: async (projectId: string, payload: StoryboardGeneratePayload): Promise<StoryboardGenerationJob> => {
    const { data } = await api.post<StoryboardGenerationJob>(`/projects/${projectId}/storyboard/generate`, payload)
    return data
  },

  getStoryboard: async (
    projectId: string,
    params?: { mode?: string; sequence_id?: string; scene_number?: number }
  ): Promise<StoryboardScopeResponse> => {
    const { data } = await api.get<StoryboardScopeResponse>(`/projects/${projectId}/storyboard`, { params })
    return data
  },

  getSequenceStoryboard: async (projectId: string, sequenceId: string): Promise<StoryboardSequenceDetail> => {
    const { data } = await api.get<StoryboardSequenceDetail>(`/projects/${projectId}/storyboard/sequences/${sequenceId}`)
    return data
  },

  regenerateSequence: async (
    projectId: string,
    sequenceId: string,
    payload: Pick<StoryboardGeneratePayload, 'style_preset' | 'shots_per_scene'>
  ): Promise<{
    job_id: string
    mode: string
    sequence_id?: string | null
    version: number
    style_preset: string
    shots_per_scene: number
  }> => {
    const { data } = await api.post(`/projects/${projectId}/storyboard/sequences/${sequenceId}/regenerate`, payload)
    return data
  },
}

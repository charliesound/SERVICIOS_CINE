import api from './client'
import type {
  FullScriptAnalysisResult,
  SequenceStoryboardPlan,
  ShotFeedbackRequest,
  StoryboardRevisionResult,
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

  analyzeFullScript: async (projectId: string): Promise<FullScriptAnalysisResult> => {
    const { data } = await api.post<FullScriptAnalysisResult>('/api/cid/script/analyze-full', {
      project_id: projectId,
      script_text: '',
    })
    return data
  },

  planSequence: async (projectId: string, sequenceId: string): Promise<SequenceStoryboardPlan> => {
    const { data } = await api.post<SequenceStoryboardPlan>(
      `/projects/${projectId}/storyboard/sequences/${sequenceId}/plan`,
      {}
    )
    return data
  },

  generateBySequence: async (
    projectId: string,
    sequenceId: string,
    payload: { style_preset?: string; shots_per_scene?: number; overwrite?: boolean }
  ): Promise<StoryboardGenerationJob> => {
    const { data } = await api.post<StoryboardGenerationJob>(
      `/projects/${projectId}/storyboard/sequences/${sequenceId}/generate`,
      payload
    )
    return data
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

  submitShotDirectorFeedback: async (
    projectId: string,
    shotId: string,
    payload: ShotFeedbackRequest
  ): Promise<StoryboardRevisionResult> => {
    const { data } = await api.post<StoryboardRevisionResult>(
      `/projects/${projectId}/storyboard/shots/${shotId}/feedback`,
      payload
    )
    return data
  },

  submitSequenceDirectorFeedback: async (
    projectId: string,
    sequenceId: string,
    payload: { note_text: string; apply_to: string; shot_ids?: string[]; preserve_original_logic?: boolean }
  ): Promise<StoryboardRevisionResult> => {
    const { data } = await api.post<StoryboardRevisionResult>(
      `/projects/${projectId}/storyboard/sequences/${sequenceId}/feedback`,
      payload
    )
    return data
  },

  getShotRevisionHistory: async (
    projectId: string,
    shotId: string
  ): Promise<Array<Record<string, unknown>>> => {
    const { data } = await api.get<Array<Record<string, unknown>>>(
      `/projects/${projectId}/storyboard/shots/${shotId}/revisions`
    )
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
    generated_assets: string[]
    total_shots: number
    total_scenes: number
    render_jobs: Array<{ job_id: string; backend?: string; workflow_key?: string; storyboard_shot_id?: string }>
    render_errors: Array<{ storyboard_shot_id: string; error: string }>
    created_at: string
  }> => {
    const { data } = await api.post(`/projects/${projectId}/storyboard/sequences/${sequenceId}/regenerate`, payload)
    return data
  },
}

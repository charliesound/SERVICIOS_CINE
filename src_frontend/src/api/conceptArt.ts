import api from './client'
import type { ConceptArtDryRunPayload, ConceptArtDryRunResponse, ConceptArtJobsResponse } from '@/types/conceptArt'

export const conceptArtApi = {
  compileProjectConceptArtWorkflowDryRun: async (
    projectId: string,
    payload: ConceptArtDryRunPayload
  ): Promise<ConceptArtDryRunResponse> => {
    const { data } = await api.post<ConceptArtDryRunResponse>(
      `/projects/${projectId}/concept-art/compile-workflow-dry-run`,
      payload
    )
    return data
  },

  compileProjectKeyVisualWorkflowDryRun: async (
    projectId: string,
    payload: ConceptArtDryRunPayload
  ): Promise<ConceptArtDryRunResponse> => {
    const { data } = await api.post<ConceptArtDryRunResponse>(
      `/projects/${projectId}/key-visual/compile-workflow-dry-run`,
      payload
    )
    return data
  },

  listProjectConceptArtJobs: async (
    projectId: string
  ): Promise<ConceptArtJobsResponse> => {
    const { data } = await api.get<ConceptArtJobsResponse>(
      `/projects/${projectId}/concept-art/jobs`
    )
    return data
  },
}

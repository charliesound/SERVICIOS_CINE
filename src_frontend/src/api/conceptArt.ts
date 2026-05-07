import api from './client'
import type { ConceptArtDryRunPayload, ConceptArtDryRunResponse } from '@/types/conceptArt'

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
}

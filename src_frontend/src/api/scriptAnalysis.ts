import api from './client'
import type { ScriptAnalysisExportFormat, ScriptAnalysisSummary } from '@/types/scriptAnalysis'

export const scriptAnalysisApi = {
  runAnalysis: async (projectId: string): Promise<{
    breakdown_id: string
    status: string
    scenes_count: number
    characters_count: number
    locations_count: number
  }> => {
    const { data } = await api.post(`/projects/${projectId}/analysis/run`)
    return data
  },

  getSummary: async (projectId: string): Promise<ScriptAnalysisSummary> => {
    const { data } = await api.get(`/projects/${projectId}/analysis/summary`)
    return data as ScriptAnalysisSummary
  },

  exportAnalysis: async (
    projectId: string,
    format: ScriptAnalysisExportFormat,
  ): Promise<Blob> => {
    const { data } = await api.get(`/projects/${projectId}/analysis/export`, {
      params: { format },
      responseType: 'blob',
    })
    return data
  },

  getModuleStatus: async (projectId: string): Promise<{
    module_key: string
    enabled: boolean
    status: string
  }> => {
    const { data } = await api.get(`/projects/${projectId}/module-status`)
    return data
  },
}

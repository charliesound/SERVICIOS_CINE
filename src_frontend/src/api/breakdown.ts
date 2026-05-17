import api from './client'
import type {
  BreakdownScenesResponse,
  BreakdownDepartmentsResponse,
  BreakdownExportFormat,
} from '../types/breakdown'

export const breakdownApi = {
  getBreakdownScenes: async (projectId: string): Promise<BreakdownScenesResponse> => {
    const { data } = await api.get(`/projects/${projectId}/breakdown/scenes`)
    return data
  },
  getBreakdownDepartments: async (projectId: string): Promise<BreakdownDepartmentsResponse> => {
    const { data } = await api.get(`/projects/${projectId}/breakdown/departments`)
    return data
  },
  exportBreakdown: async (projectId: string, format: BreakdownExportFormat): Promise<Blob> => {
    const { data } = await api.get(`/projects/${projectId}/breakdown/export?format=${format}`, {
      responseType: 'blob',
    })
    return data
  },
}

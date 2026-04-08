import api from './client'
import { WorkflowCatalogItem, IntentAnalysis, WorkflowPlanRequest, Preset, PresetCreate } from '@/types'

export const workflowApi = {
  getCatalog: async (): Promise<WorkflowCatalogItem[]> => {
    const { data } = await api.get<WorkflowCatalogItem[]>('/workflows/catalog')
    return data
  },

  planWorkflow: async (request: WorkflowPlanRequest): Promise<IntentAnalysis> => {
    const { data } = await api.post<IntentAnalysis>('/workflows/plan', request)
    return data
  },

  buildWorkflow: async (workflowKey: string, inputs: Record<string, any>): Promise<Record<string, any>> => {
    const { data } = await api.post('/workflows/build', { workflow_key: workflowKey, inputs })
    return data
  },

  validateWorkflow: async (workflow: Record<string, any>, strict?: boolean) => {
    const { data } = await api.post('/workflows/validate', { workflow, strict })
    return data
  },

  getPresets: async (params?: { user_id?: string; category?: string }): Promise<Preset[]> => {
    const { data } = await api.get<Preset[]>('/workflows/presets', { params })
    return data
  },

  getPreset: async (presetId: string): Promise<Preset> => {
    const { data } = await api.get<Preset>(`/workflows/presets/${presetId}`)
    return data
  },

  createPreset: async (preset: PresetCreate, userId: string): Promise<Preset> => {
    const { data } = await api.post<Preset>('/workflows/presets', preset, { params: { user_id: userId } })
    return data
  },
}

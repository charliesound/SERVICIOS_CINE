import api from './client'
import { InstanceStatus, CapabilitiesResponse, BackendCapabilities } from '@/types'

export const opsApi = {
  getInstances: async (): Promise<InstanceStatus> => {
    const { data } = await api.get<InstanceStatus>('/ops/instances')
    return data
  },

  getInstance: async (backend: string): Promise<any> => {
    const { data } = await api.get(`/ops/instances/${backend}`)
    return data
  },

  getCapabilities: async (forceRefresh?: boolean): Promise<CapabilitiesResponse> => {
    const { data } = await api.get<CapabilitiesResponse>('/ops/capabilities', {
      params: { force_refresh: forceRefresh },
    })
    return data
  },

  getBackendCapabilities: async (backend: string, forceRefresh?: boolean): Promise<BackendCapabilities> => {
    const { data } = await api.get<BackendCapabilities>(`/ops/capabilities/${backend}`, {
      params: { force_refresh: forceRefresh },
    })
    return data
  },

  healthCheck: async (backend: string): Promise<{ healthy: boolean }> => {
    const { data } = await api.post(`/ops/instances/${backend}/health-check`)
    return data
  },

  canRunWorkflow: async (backend: string, capabilities: string[]): Promise<any> => {
    const { data } = await api.get('/ops/can-run', {
      params: { backend, capabilities: capabilities.join(',') },
    })
    return data
  },

  getSchedulerStatus: async (): Promise<any> => {
    const { data } = await api.get('/admin/scheduler/status')
    return data
  },

  getSystemOverview: async (): Promise<any> => {
    const { data } = await api.get('/admin/system/overview')
    return data
  },
}

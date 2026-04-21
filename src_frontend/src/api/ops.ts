import api from './client'
import { InstanceStatus, CapabilitiesResponse, BackendCapabilities } from '@/types'

export interface AdminProjectSummary {
  id: string
  name: string
  organization_id: string
  created_at: string
}

export interface AdminJobSummary {
  id: string
  project_id: string
  job_type: string
  status: string
  created_at: string
}

export interface AdminOrganizationSummary {
  id: string
  name: string
  project_count: number
  job_count: number
}

export interface AdminSchedulerStatus {
  running: boolean
  poll_interval: number
  job_timeout: number
  queue_status?: Record<string, unknown>
}

export interface AdminSystemOverview {
  timestamp: string
  scheduler: AdminSchedulerStatus
  queue: Record<string, { queue_size?: number; running?: number; max_concurrent?: number; items?: unknown[] }>
  backends: Record<string, unknown>
  summary: {
    total_backends: number
    available_backends: number
    total_running: number
    total_queued: number
  }
}

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

  getSchedulerStatus: async (): Promise<AdminSchedulerStatus> => {
    const { data } = await api.get<AdminSchedulerStatus>('/admin/scheduler/status')
    return data
  },

  getSystemOverview: async (): Promise<AdminSystemOverview> => {
    const { data } = await api.get<AdminSystemOverview>('/admin/system/overview')
    return data
  },

  getAdminProjects: async (): Promise<AdminProjectSummary[]> => {
    const { data } = await api.get<AdminProjectSummary[]>('/admin/projects')
    return data
  },

  getAdminJobs: async (): Promise<AdminJobSummary[]> => {
    const { data } = await api.get<AdminJobSummary[]>('/admin/jobs')
    return data
  },

  getAdminOrganizations: async (): Promise<AdminOrganizationSummary[]> => {
    const { data } = await api.get<AdminOrganizationSummary[]>('/admin/organizations')
    return data
  },
}

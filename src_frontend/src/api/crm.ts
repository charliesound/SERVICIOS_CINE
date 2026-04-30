import api from './client'

export interface CRMContact {
  id: string
  contact_type: string
  company_name: string | null
  contact_name: string | null
  role_title: string | null
  email: string | null
  phone: string | null
  website: string | null
  country: string | null
  region: string | null
  notes: string | null
  status: string
}

export interface CRMOpportunity {
  id: string
  project_id: string
  contact_id: string | null
  opportunity_type: string
  status: string
  priority: string
  fit_score: number
  next_action: string | null
  next_action_date: string | null
  pitch_pack_id: string | null
  distribution_pack_id: string | null
  notes: string | null
}

export interface CRMCommunication {
  id: string
  contact_id: string
  opportunity_id: string | null
  communication_type: string
  direction: string
  subject: string | null
  body: string | null
  occurred_at: string | null
}

export interface CRMTask {
  id: string
  project_id: string
  opportunity_id: string | null
  title: string
  description: string | null
  status: string
  priority: string
  due_date: string | null
}

export interface CRMSummary {
  total_opportunities: number
  total_tasks: number
  opportunities_by_status: Record<string, number>
  interested_count: number
  pending_count: number
}

export const crmApi = {
  listContacts: async (contactType?: string, status?: string): Promise<{ contacts: CRMContact[] }> => {
    const params = new URLSearchParams()
    if (contactType) params.set('contact_type', contactType)
    if (status) params.set('status', status)
    const { data } = await api.get<{ contacts: CRMContact[] }>(`/crm/contacts?${params.toString()}`)
    return data
  },

  createContact: async (payload: Partial<CRMContact>): Promise<{ contact_id: string }> => {
    const { data } = await api.post<{ contact_id: string }>('/crm/contacts', payload)
    return data
  },

  getContact: async (contactId: string): Promise<{ contact: CRMContact }> => {
    const { data } = await api.get<{ contact: CRMContact }>(`/crm/contacts/${contactId}`)
    return data
  },

  updateContact: async (contactId: string, payload: Partial<CRMContact>): Promise<{ contact_id: string }> => {
    const { data } = await api.patch<{ contact_id: string }>(`/crm/contacts/${contactId}`, payload)
    return data
  },

  archiveContact: async (contactId: string): Promise<{ contact_id: string }> => {
    const { data } = await api.post<{ contact_id: string }>(`/crm/contacts/${contactId}/archive`, {})
    return data
  },

  getCrmSummary: async (projectId: string): Promise<CRMSummary> => {
    const { data } = await api.get<CRMSummary>(`/projects/${projectId}/crm/summary`)
    return data
  },

  listOpportunities: async (projectId: string, status?: string, priority?: string): Promise<{ opportunities: CRMOpportunity[] }> => {
    const params = new URLSearchParams()
    if (status) params.set('status', status)
    if (priority) params.set('priority', priority)
    const { data } = await api.get<{ opportunities: CRMOpportunity[] }>(
      `/projects/${projectId}/crm/opportunities?${params.toString()}`
    )
    return data
  },

  createOpportunity: async (projectId: string, payload: Partial<CRMOpportunity>): Promise<{ opportunity_id: string }> => {
    const { data } = await api.post<{ opportunity_id: string }>(
      `/projects/${projectId}/crm/opportunities`,
      payload
    )
    return data
  },

  updateOpportunity: async (projectId: string, opportunityId: string, payload: Partial<CRMOpportunity>): Promise<{ opportunity_id: string }> => {
    const { data } = await api.patch<{ opportunity_id: string }>(
      `/projects/${projectId}/crm/opportunities/${opportunityId}`,
      payload
    )
    return data
  },

  updateOpportunityStatus: async (projectId: string, opportunityId: string, status: string): Promise<{ opportunity_id: string }> => {
    const { data } = await api.post<{ opportunity_id: string }>(
      `/projects/${projectId}/crm/opportunities/${opportunityId}/status?status=${status}`,
      {}
    )
    return data
  },

  listCommunications: async (projectId: string, opportunityId?: string): Promise<{ communications: CRMCommunication[] }> => {
    const params = new URLSearchParams()
    if (opportunityId) params.set('opportunity_id', opportunityId)
    const { data } = await api.get<{ communications: CRMCommunication[] }>(
      `/projects/${projectId}/crm/communications?${params.toString()}`
    )
    return data
  },

  addCommunication: async (projectId: string, contactId: string, payload: Partial<CRMCommunication>): Promise<{ communication_id: string }> => {
    const { data } = await api.post<{ communication_id: string }>(
      `/projects/${projectId}/crm/communications?contact_id=${contactId}`,
      payload
    )
    return data
  },

  listTasks: async (projectId: string, status?: string): Promise<{ tasks: CRMTask[] }> => {
    const params = new URLSearchParams()
    if (status) params.set('status', status)
    const { data } = await api.get<{ tasks: CRMTask[] }>(`/projects/${projectId}/crm/tasks?${params.toString()}`)
    return data
  },

  createTask: async (projectId: string, payload: Partial<CRMTask>): Promise<{ task_id: string }> => {
    const { data } = await api.post<{ task_id: string }>(`/projects/${projectId}/crm/tasks`, payload)
    return data
  },

  completeTask: async (projectId: string, taskId: string): Promise<{ task_id: string }> => {
    const { data } = await api.post<{ task_id: string }>(`/projects/${projectId}/crm/tasks/${taskId}/complete`, {})
    return data
  },

  cancelTask: async (projectId: string, taskId: string): Promise<{ task_id: string }> => {
    const { data } = await api.post<{ task_id: string }>(`/projects/${projectId}/crm/tasks/${taskId}/cancel`, {})
    return data
  },
}
import api from './client'

export interface Project {
  id: string
  organization_id: string
  name: string
  description?: string
  status: string
  script_text?: string
}

export interface CreateProjectPayload {
  name: string
  description?: string
}

export interface UpdateScriptPayload {
  script_text: string
}

export interface ProjectJob {
  id: string
  organization_id: string
  project_id: string
  job_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  result_data: Record<string, unknown> | null
  error_message: string | null
  progress_percent?: number | null
  progress_stage?: string | null
  progress_code?: string | null
  created_by: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
}

export const projectsApi = {
  list: async (): Promise<{ projects: Project[] }> => {
    const { data } = await api.get<{ projects: Project[] }>('/projects')
    return data
  },

  create: async (payload: CreateProjectPayload): Promise<Project> => {
    const { data } = await api.post<Project>('/projects', payload)
    return data
  },

  get: async (projectId: string): Promise<Project> => {
    const { data } = await api.get<Project>(`/projects/${projectId}`)
    return data
  },

  updateScript: async (projectId: string, payload: UpdateScriptPayload): Promise<Project> => {
    const { data } = await api.put<Project>(`/projects/${projectId}/script`, payload)
    return data
  },

  intakeScript: async (projectId: string, payload: UpdateScriptPayload): Promise<{ project_id: string; message: string }> => {
    const { data } = await api.post<{ project_id: string; message: string }>(`/projects/${projectId}/intake/script`, payload)
    return data
  },

  uploadScriptDocument: async (
    projectId: string,
    file: File,
    documentType = 'script',
    visibilityScope = 'project',
  ): Promise<{
    id: string
    file_name: string
    mime_type: string
    extracted_text?: string | null
    upload_status: string
    error_message?: string | null
  }> => {
    const formData = new FormData()
    formData.append('document_type', documentType)
    formData.append('visibility_scope', visibilityScope)
    formData.append('file', file)
    const { data } = await api.post(`/projects/${projectId}/documents`, formData)
    return data
  },

  analyze: async (projectId: string): Promise<{
    document_id: string
    doc_type: string
    confidence_score: number | null
    structured_payload: Record<string, unknown>
  }> => {
    const { data } = await api.post(`/projects/${projectId}/analyze`)
    return data
  },

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

  getAnalysisSummary: async (projectId: string): Promise<Record<string, unknown>> => {
    const { data } = await api.get(`/projects/${projectId}/analysis/summary`)
    return data
  },

  getBreakdownScenes: async (projectId: string): Promise<{ project_id: string; scenes: Array<Record<string, unknown>> }> => {
    const { data } = await api.get(`/projects/${projectId}/breakdown/scenes`)
    return data
  },

  getBreakdownDepartments: async (projectId: string): Promise<Record<string, unknown>> => {
    const { data } = await api.get(`/projects/${projectId}/breakdown/departments`)
    return data
  },

  storyboard: async (projectId: string): Promise<{
    project_id: string
    total_scenes: number
    scenes: Array<{
      scene_number: number
      heading: string
      location: string
      time_of_day: string
      shots: Array<{ shot_number: number; shot_type: string; description: string }>
    }>
  }> => {
    const { data } = await api.post(`/projects/${projectId}/storyboard`)
    return data
  },

  getJobs: async (projectId: string): Promise<ProjectJob[]> => {
    const { data } = await api.get<{ jobs: ProjectJob[] }>(`/projects/${projectId}/jobs`)
    return data.jobs
  },

  retryJob: async (projectId: string, jobId: string): Promise<ProjectJob> => {
    const { data } = await api.post<ProjectJob>(`/projects/${projectId}/jobs/${jobId}/retry`)
    return data
  },

  getAssets: async (projectId: string): Promise<Array<{
    id: string; project_id: string; job_id: string | null;
    file_name: string; file_extension: string; asset_type: string;
    asset_source: string | null; content_ref?: string | null;
    metadata_json?: Record<string, unknown> | null;
    status: string; created_at: string | null;
  }>> => {
    const { data } = await api.get<{ assets: Array<{
      id: string; project_id: string; job_id: string | null;
      file_name: string; file_extension: string; asset_type: string;
      asset_source: string | null; content_ref?: string | null;
      metadata_json?: Record<string, unknown> | null;
      status: string; created_at: string | null;
    }> }>(`/projects/${projectId}/assets`)
    return data.assets
  },

  exportJson: async (projectId: string): Promise<Blob> => {
    const { data } = await api.get(`/projects/${projectId}/export/json`, {
      responseType: 'blob',
    })
    return data
  },

  triggerExport: async (projectId: string): Promise<{ job_id: string; status: string }> => {
    const { data } = await api.post<{ job_id: string; status: string }>(`/delivery/projects/${projectId}/export`)
    return data
  },

  getJobStatus: async (jobId: string): Promise<{ id: string; status: string; result_data: Record<string, unknown> | null }> => {
    const { data } = await api.get(`/projects/jobs/${jobId}`)
    return data
  },

  getJobProgress: async (projectId: string, jobId: string): Promise<{
    job_id: string
    job_type: string
    status: string
    progress_percent: number
    progress_stage: string
    progress_code: string
    updated_at: string | null
  }> => {
    const { data } = await api.get(`/projects/${projectId}/jobs/${jobId}/progress`)
    return data
  },

  downloadDeliverable: async (deliverableId: string): Promise<Blob> => {
    const { data } = await api.get(`/delivery/deliverables/${deliverableId}/download`, {
      responseType: 'blob',
    })
    return data
  },

  // Legacy/Direct export (might still work for some backends, but ZIP is now async)
  exportZip: async (projectId: string): Promise<Blob> => {
    const { data } = await api.get(`/projects/${projectId}/export/zip`, {
      responseType: 'blob',
    })
    return data
  },
}

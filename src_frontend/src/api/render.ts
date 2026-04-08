import api from './client'
import { JobCreate, JobResponse, JobDetail } from '@/types'

export const renderApi = {
  createJob: async (job: JobCreate): Promise<JobResponse> => {
    const { data } = await api.post<JobResponse>('/render/jobs', job)
    return data
  },

  getJob: async (jobId: string): Promise<JobDetail> => {
    const { data } = await api.get<JobDetail>(`/render/jobs/${jobId}`)
    return data
  },

  listJobs: async (params?: { user_id?: string; backend?: string }): Promise<JobDetail[]> => {
    const { data } = await api.get<JobDetail[]>('/render/jobs', { params })
    return data
  },

  retryJob: async (jobId: string): Promise<JobResponse> => {
    const { data } = await api.post<JobResponse>(`/render/jobs/${jobId}/retry`)
    return data
  },
}

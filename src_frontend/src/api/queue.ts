import api from './client'
import { FullQueueStatus, QueueItem } from '@/types'

export const queueApi = {
  getStatus: async (): Promise<FullQueueStatus> => {
    const { data } = await api.get<FullQueueStatus>('/queue/status')
    return data
  },

  getJobStatus: async (jobId: string): Promise<QueueItem> => {
    const { data } = await api.get<QueueItem>(`/queue/status/${jobId}`)
    return data
  },

  cancelJob: async (jobId: string): Promise<void> => {
    await api.post(`/queue/${jobId}/cancel`)
  },

  retryJob: async (jobId: string): Promise<void> => {
    await api.post(`/queue/${jobId}/retry`)
  },
}

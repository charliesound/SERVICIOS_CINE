import { useQuery } from '@tanstack/react-query'
import { queueApi } from '@/api'

export function useQueueStatus() {
  return useQuery({
    queryKey: ['queue'],
    queryFn: queueApi.getStatus,
    refetchInterval: 5000,
  })
}

export function useJobQueueStatus(jobId: string) {
  return useQuery({
    queryKey: ['queueJob', jobId],
    queryFn: () => queueApi.getJobStatus(jobId),
    enabled: !!jobId,
    refetchInterval: 3000,
  })
}

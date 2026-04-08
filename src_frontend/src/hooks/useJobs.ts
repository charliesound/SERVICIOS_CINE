import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { renderApi } from '@/api'
import { JobCreate } from '@/types'

export function useJobs(params?: { user_id?: string; backend?: string }) {
  return useQuery({
    queryKey: ['jobs', params],
    queryFn: () => renderApi.listJobs(params),
    refetchInterval: 5000,
  })
}

export function useJob(jobId: string) {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => renderApi.getJob(jobId),
    enabled: !!jobId,
    refetchInterval: 3000,
  })
}

export function useCreateJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (job: JobCreate) => renderApi.createJob(job),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['queue'] })
    },
  })
}

export function useRetryJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (jobId: string) => renderApi.retryJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['queue'] })
    },
  })
}

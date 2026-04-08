export type QueueStatus = 'queued' | 'scheduled' | 'running' | 'succeeded' | 'failed' | 'timeout' | 'canceled' | 'rejected'

export interface QueueItem {
  job_id: string
  status: QueueStatus
  backend: string
  priority: number
  created_at: string
  queue_position?: number
}

export interface BackendQueueStatus {
  queue_size: number
  running: number
  max_concurrent: number
  items: QueueItem[]
}

export interface FullQueueStatus {
  backends: Record<string, BackendQueueStatus>
  timestamp: string
}

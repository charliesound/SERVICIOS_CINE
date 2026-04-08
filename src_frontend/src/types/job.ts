export type TaskType = 'still' | 'video' | 'dubbing' | 'experimental'
export type JobStatus = 'pending' | 'queued' | 'scheduled' | 'running' | 'succeeded' | 'failed' | 'timeout' | 'canceled' | 'rejected'

export interface JobCreate {
  task_type: TaskType
  workflow_key: string
  prompt: Record<string, any>
  user_id: string
  user_plan: string
  priority?: number
  target_instance?: string
}

export interface JobResponse {
  job_id: string
  status: JobStatus
  backend: string
  backend_url: string
  queue_position?: number
  estimated_time?: number
  error?: string
}

export interface JobDetail {
  job_id: string
  task_type: string
  workflow_key: string
  status: JobStatus
  backend: string
  created_at: string
  started_at?: string
  completed_at?: string
  error?: string
}

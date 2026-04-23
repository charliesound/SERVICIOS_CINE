export interface User {
  user_id: string
  username: string
  email: string
  plan: string
  role: string
  is_active: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserPlanStatus {
  plan: string
  active_jobs: number
  max_active_jobs: number
  queued_jobs: number
  max_queued_jobs: number
  can_submit_active: boolean
  can_submit_queued: boolean
  priority_score: number
  projects_count: number
  jobs_count: number
  analyses_count: number
  storyboards_count: number
  max_projects: number
  max_total_jobs: number
  max_analyses: number
  max_storyboards: number
  export_json: boolean
  export_zip: boolean
  recommended_upgrade?: string | null
}

export interface PlanInfo {
  id: string
  name: string
  display_name: string
  price: number
  billing_period: string
  limits: {
    max_active_jobs: number
    max_queued_jobs: number
    priority_score: number
    max_projects: number
    max_total_jobs: number
    max_analyses: number
    max_storyboards: number
    export_json: boolean
    export_zip: boolean
    allowed_task_types: string[]
  }
  features: string[]
}

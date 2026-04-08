export interface BackendInstance {
  name: string
  type: string
  host: string
  port: number
  base_url: string
  enabled: boolean
  healthy: boolean
  current_jobs: number
  max_concurrent_jobs: number
  available_slots: number
  capabilities: string[]
}

export interface InstanceStatus {
  total_backends: number
  available_backends: number
  backends: Record<string, BackendInstance>
}

export interface BackendCapabilities {
  backend: string
  healthy: boolean
  response_time_ms: number
  comfyui_version?: string
  nodes_count: number
  models_count: number
  nodes: {
    type: string
    category: string
    inputs: string[]
    outputs: string[]
  }[]
  models: {
    name: string
    type: string
    loaded: boolean
    size_mb?: number
  }[]
  detected_capabilities: string[]
  warnings: string[]
  last_check: string
}

export interface CapabilitiesResponse {
  backends: Record<string, BackendCapabilities>
  timestamp: string
}

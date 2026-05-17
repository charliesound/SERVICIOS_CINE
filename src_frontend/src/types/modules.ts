export interface ModuleInfo {
  key: string
  name: string
  short_description: string
  category: string
  status: string
  commercial_status: string
  requires_gpu: boolean
  requires_local_gpu_node: boolean
  default_enabled: boolean
  visible_in_catalog: boolean
  dependencies: string[]
  recommended_pack?: string | null
  route_prefixes: string[]
  feature_flag_key?: string | null
}

export interface ModuleAccessInfo extends ModuleInfo {
  enabled: boolean
  locked_reason?: string | null
}

export interface ModuleCatalogResponse {
  modules: ModuleInfo[]
  total: number
}

export interface UserModulesResponse {
  plan: string
  organization_id?: string | null
  available_modules: ModuleAccessInfo[]
  locked_modules: ModuleAccessInfo[]
  total_available: number
  total_locked: number
}

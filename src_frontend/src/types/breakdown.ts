export type BreakdownExportFormat = 'json' | 'csv' | 'md'

export interface BreakdownScene {
  scene_number?: number | string
  heading?: string
  location?: string
  time_of_day?: string
  int_ext?: string
  characters?: string[]
  props?: string[]
  [key: string]: unknown
}

export interface BreakdownDepartment {
  department?: string
  items?: string[]
  [key: string]: unknown
}

export interface BreakdownScenesResponse {
  scenes: BreakdownScene[]
}

export interface BreakdownDepartmentsResponse {
  departments: BreakdownDepartment[]
}

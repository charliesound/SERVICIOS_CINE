import api from './client'

export interface BudgetEstimate {
  id: string
  project_id: string
  title: string
  currency: string
  budget_level: string
  status: string
  total_min: number
  total_estimated: number
  total_max: number
  contingency_percent: number
  assumptions_json: string[]
  role_summaries_json: Record<string, unknown>
  role_summary?: Record<string, unknown>
  created_at: string
}

export interface BudgetLine {
  id: string
  category: string
  subcategory: string | null
  description: string | null
  unit: string | null
  quantity: number
  unit_cost_min: number
  unit_cost_estimated: number
  unit_cost_max: number
  total_min: number
  total_estimated: number
  total_max: number
  source: string
  confidence: string
  notes: string | null
}

export interface GenerateBudgetPayload {
  level?: string
  script_text?: string
}

export interface RecalculatePayload {
  level: string
}

export const budgetsApi = {
  list: async (projectId: string): Promise<{ budgets: BudgetEstimate[] }> => {
    const { data } = await api.get<{ budgets: BudgetEstimate[] }>(
      `/projects/${projectId}/budgets`
    )
    return data
  },

  generate: async (
    projectId: string,
    payload: GenerateBudgetPayload
  ): Promise<{ budget: BudgetEstimate }> => {
    const { data } = await api.post<{ budget: BudgetEstimate }>(
      `/projects/${projectId}/budgets/generate`,
      payload
    )
    return data
  },

  getActive: async (
    projectId: string,
    role?: string
  ): Promise<{ budget: BudgetEstimate }> => {
    const params = role ? `?role=${role}` : ''
    const { data } = await api.get<{ budget: BudgetEstimate }>(
      `/projects/${projectId}/budgets/active${params}`
    )
    return data
  },

  get: async (
    projectId: string,
    budgetId: string,
    role?: string
  ): Promise<{ budget: BudgetEstimate; lines: BudgetLine[] }> => {
    const params = role ? `?role=${role}` : ''
    const { data } = await api.get<{ budget: BudgetEstimate; lines: BudgetLine[] }>(
      `/projects/${projectId}/budgets/${budgetId}${params}`
    )
    return data
  },

  activate: async (
    projectId: string,
    budgetId: string
  ): Promise<{ budget: BudgetEstimate }> => {
    const { data } = await api.post<{ budget: BudgetEstimate }>(
      `/projects/${projectId}/budgets/${budgetId}/activate`
    )
    return data
  },

  recalculate: async (
    projectId: string,
    budgetId: string,
    payload: RecalculatePayload
  ): Promise<{ budget: BudgetEstimate }> => {
    const { data } = await api.post<{ budget: BudgetEstimate }>(
      `/projects/${projectId}/budgets/${budgetId}/recalculate`,
      payload
    )
    return data
  },

  archive: async (
    projectId: string,
    budgetId: string
  ): Promise<{ budget: BudgetEstimate }> => {
    const { data } = await api.post<{ budget: BudgetEstimate }>(
      `/projects/${projectId}/budgets/${budgetId}/archive`
    )
    return data
  },

  exportJson: async (projectId: string, budgetId: string): Promise<string> => {
    const { data } = await api.get<string>(
      `/projects/${projectId}/budgets/${budgetId}/export/json`
    )
    return data
  },

  exportCsv: async (projectId: string, budgetId: string): Promise<string> => {
    const { data } = await api.get<string>(
      `/projects/${projectId}/budgets/${budgetId}/export/csv`
    )
    return data
  },
}
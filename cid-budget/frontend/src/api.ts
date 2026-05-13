const API_BASE = import.meta.env.VITE_API_URL || ''
const API = `${API_BASE}/api/budget`

async function req<T>(url: string, opts?: RequestInit): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${API}${url}`, { headers, ...opts })
  if (res.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`HTTP ${res.status}: ${body}`)
  }
  return res.json()
}

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
  assumptions: string[]
  created_at: string
}

export interface BudgetLine {
  id: string
  category: string
  description: string
  unit: string
  quantity: number
  unit_cost_min: number
  unit_cost_estimated: number
  unit_cost_max: number
  total_min: number
  total_estimated: number
  total_max: number
  confidence: string
}

export const budgetsApi = {
  list: (projectId: string) => req<{ budgets: BudgetEstimate[] }>(`/projects/${encodeURIComponent(projectId)}`),
  getActive: (projectId: string) => req<{ budget: BudgetEstimate | null }>(`/projects/${encodeURIComponent(projectId)}/active`),
  get: (budgetId: string) => req<{ budget: BudgetEstimate; lines: BudgetLine[] }>(`/${encodeURIComponent(budgetId)}`),
  generate: (projectId: string, level = 'medium', scriptText = '') =>
    req<{ budget: BudgetEstimate }>(`/projects/${encodeURIComponent(projectId)}/generate?level=${level}&script_text=${encodeURIComponent(scriptText)}`, { method: 'POST' }),
  activate: (budgetId: string) => req<{ budget: BudgetEstimate }>(`/${encodeURIComponent(budgetId)}/activate`, { method: 'POST' }),
  recalculate: (budgetId: string, level: string) =>
    req<{ budget: BudgetEstimate }>(`/${encodeURIComponent(budgetId)}/recalculate?level=${level}`, { method: 'POST' }),
  archive: (budgetId: string) => req<{ budget: BudgetEstimate }>(`/${encodeURIComponent(budgetId)}/archive`, { method: 'POST' }),
}

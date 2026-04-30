import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

interface DashboardModule {
  status: string
  summary: string
  action?: string
  route?: string
  count?: number
}

interface RecommendedAction {
  label: string
  route: string
  priority: string
  permission?: string
  locked?: boolean
  reason?: string
}

interface RoleDashboard {
  active_role: string
  available_roles: string[]
  permissions: string[]
  user_role: string
}

interface ProjectDashboard {
  project_id: string
  title: string
  status: string
  overall_progress: number
  modules: Record<string, DashboardModule>
  recommended_next_actions: RecommendedAction[]
  warnings: string[]
  role_dashboard?: RoleDashboard
}

export function useProjectDashboard(projectId: string, role?: string) {
  return useQuery({
    queryKey: ['project-dashboard', projectId, role],
    queryFn: async (): Promise<ProjectDashboard> => {
      const params = role ? { role } : {}
      const { data } = await axios.get(`/api/projects/${projectId}/dashboard`, { params })
      return data
    },
    enabled: !!projectId,
  })
}

export function getPermissionBadge(permission: string, permissions: string[]): string {
  return permissions.includes(permission) ? 'green' : 'gray'
}

export function canAccess(permission: string, permissions: string[]): boolean {
  return permissions.includes(permission)
}
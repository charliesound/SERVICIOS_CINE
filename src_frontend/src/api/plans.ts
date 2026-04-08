import api from './client'
import { PlanInfo, UserPlanStatus } from '@/types'

export const plansApi = {
  getCatalog: async (): Promise<PlanInfo[]> => {
    const { data } = await api.get<PlanInfo[]>('/plans/catalog')
    return data
  },

  getMyPlan: async (userId: string, planName: string): Promise<UserPlanStatus> => {
    const { data } = await api.get<UserPlanStatus>('/plans/me', {
      params: { user_id: userId, plan_name: planName },
    })
    return data
  },

  getPlanDetails: async (planName: string): Promise<PlanInfo> => {
    const { data } = await api.get<PlanInfo>(`/plans/${planName}`)
    return data
  },

  canRunTask: async (planName: string, taskType: string): Promise<boolean> => {
    const { data } = await api.get<{ allowed: boolean }>(`/plans/${planName}/can-run/${taskType}`)
    return data.allowed
  },
}

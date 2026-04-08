import { useQuery } from '@tanstack/react-query'
import { plansApi } from '@/api'

export function usePlansCatalog() {
  return useQuery({
    queryKey: ['plansCatalog'],
    queryFn: plansApi.getCatalog,
  })
}

export function useUserPlanStatus(userId: string, planName: string) {
  return useQuery({
    queryKey: ['userPlan', userId, planName],
    queryFn: () => plansApi.getMyPlan(userId, planName),
    enabled: !!userId,
    refetchInterval: 30000,
  })
}

export function usePlanDetails(planName: string) {
  return useQuery({
    queryKey: ['planDetails', planName],
    queryFn: () => plansApi.getPlanDetails(planName),
    enabled: !!planName,
  })
}

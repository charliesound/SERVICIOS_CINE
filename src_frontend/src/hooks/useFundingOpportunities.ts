import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { projectFundingApi, type FundingMatchListParams } from '@/api'

const fundingOpportunityKeys = {
  profile: (projectId: string) => ['fundingProfile', projectId] as const,
  checklist: (projectId: string) => ['fundingChecklist', projectId] as const,
  matcherStatus: (projectId: string) => ['fundingMatcherStatus', projectId] as const,
  matches: (projectId: string, params: FundingMatchListParams) => ['fundingMatchesRag', projectId, params] as const,
  evidence: (projectId: string, matchId: string) => ['fundingMatchEvidence', projectId, matchId] as const,
}

export function useFundingProfile(projectId: string) {
  return useQuery({
    queryKey: fundingOpportunityKeys.profile(projectId),
    queryFn: () => projectFundingApi.getProfile(projectId),
    enabled: !!projectId,
  })
}

export function useFundingChecklist(projectId: string) {
  return useQuery({
    queryKey: fundingOpportunityKeys.checklist(projectId),
    queryFn: () => projectFundingApi.getChecklist(projectId),
    enabled: !!projectId,
  })
}

export function useFundingMatcherStatus(projectId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: fundingOpportunityKeys.matcherStatus(projectId),
    queryFn: () => projectFundingApi.getMatcherStatus(projectId),
    enabled: !!projectId && enabled,
    refetchInterval: (query) => {
      const status = query.state.data?.job?.status
      return status === 'queued' || status === 'processing' ? 2500 : false
    },
  })
}

export function useFundingMatches(projectId: string, params: FundingMatchListParams) {
  return useQuery({
    queryKey: fundingOpportunityKeys.matches(projectId, params),
    queryFn: () => projectFundingApi.getRagMatches(projectId, params),
    enabled: !!projectId,
    placeholderData: (previousData) => previousData,
  })
}

export function useFundingMatchEvidence(projectId: string, matchId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: fundingOpportunityKeys.evidence(projectId, matchId),
    queryFn: () => projectFundingApi.getMatchEvidence(projectId, matchId),
    enabled: !!projectId && !!matchId && enabled,
  })
}

export function useRecomputeFundingMatches(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => projectFundingApi.recomputeRag(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fundingMatcherStatus', projectId] })
      queryClient.invalidateQueries({ queryKey: ['fundingMatchesRag', projectId] })
      queryClient.invalidateQueries({ queryKey: ['fundingChecklist', projectId] })
    },
  })
}

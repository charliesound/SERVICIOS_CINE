import { useQuery } from '@tanstack/react-query'
import { opsApi } from '@/api'

export function useInstances() {
  return useQuery({
    queryKey: ['instances'],
    queryFn: opsApi.getInstances,
    refetchInterval: 30000,
  })
}

export function useCapabilities(forceRefresh?: boolean) {
  return useQuery({
    queryKey: ['capabilities', forceRefresh],
    queryFn: () => opsApi.getCapabilities(forceRefresh),
    refetchInterval: 60000,
  })
}

export function useBackendCapabilities(backend: string, forceRefresh?: boolean) {
  return useQuery({
    queryKey: ['backendCapabilities', backend, forceRefresh],
    queryFn: () => opsApi.getBackendCapabilities(backend, forceRefresh),
    enabled: !!backend,
  })
}

export function useSystemOverview() {
  return useQuery({
    queryKey: ['systemOverview'],
    queryFn: opsApi.getSystemOverview,
    refetchInterval: 30000,
  })
}

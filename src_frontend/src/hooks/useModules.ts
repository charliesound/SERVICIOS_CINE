import { useQuery } from '@tanstack/react-query'
import { moduleCatalogApi } from '@/api'

export function useModuleCatalog() {
  return useQuery({
    queryKey: ['moduleCatalog'],
    queryFn: moduleCatalogApi.getModuleCatalog,
  })
}

export function useMyModules() {
  return useQuery({
    queryKey: ['myModules'],
    queryFn: moduleCatalogApi.getMyModules,
    retry: 1,
  })
}

export function useModuleDetail(moduleKey: string) {
  return useQuery({
    queryKey: ['moduleDetail', moduleKey],
    queryFn: () => moduleCatalogApi.getModuleDetail(moduleKey),
    enabled: !!moduleKey,
  })
}

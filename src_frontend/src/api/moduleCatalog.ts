import api from './client'
import type { ModuleCatalogResponse, ModuleInfo, UserModulesResponse } from '@/types'

export const moduleCatalogApi = {
  getModuleCatalog: async (): Promise<ModuleCatalogResponse> => {
    const { data } = await api.get<ModuleCatalogResponse>('/modules/catalog')
    return data
  },

  getMyModules: async (): Promise<UserModulesResponse> => {
    const { data } = await api.get<UserModulesResponse>('/modules/me')
    return data
  },

  getModuleDetail: async (moduleKey: string): Promise<ModuleInfo> => {
    const { data } = await api.get<ModuleInfo>(`/modules/${moduleKey}`)
    return data
  },
}

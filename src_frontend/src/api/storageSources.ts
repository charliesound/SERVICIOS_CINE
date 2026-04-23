import api from './client'
import {
  StorageAuthorization,
  StorageAuthorizationCreate,
  StorageHandshakeResult,
  StorageSource,
  StorageSourceCreate,
  StorageSourceListResponse,
  StorageSourceUpdate,
  StorageValidateRequest,
  StorageWatchPath,
  StorageWatchPathCreate,
  StorageWatchPathListResponse,
} from '@/types'

export const storageSourcesApi = {
  listStorageSources: async (params?: { project_id?: string }): Promise<StorageSource[]> => {
    const { data } = await api.get<StorageSourceListResponse>('/storage-sources', { params })
    return data.items
  },

  createStorageSource: async (payload: StorageSourceCreate): Promise<StorageSource> => {
    const { data } = await api.post<StorageSource>('/storage-sources', payload)
    return data
  },

  getStorageSource: async (sourceId: string): Promise<StorageSource> => {
    const { data } = await api.get<StorageSource>(`/storage-sources/${sourceId}`)
    return data
  },

  updateStorageSource: async (sourceId: string, payload: StorageSourceUpdate): Promise<StorageSource> => {
    const { data } = await api.patch<StorageSource>(`/storage-sources/${sourceId}`, payload)
    return data
  },

  validateStorageSource: async (sourceId: string, payload: StorageValidateRequest = {}): Promise<StorageHandshakeResult> => {
    const { data } = await api.post<StorageHandshakeResult>(`/storage-sources/${sourceId}/validate`, payload)
    return data
  },

  authorizeStorageSource: async (sourceId: string, payload: StorageAuthorizationCreate): Promise<StorageAuthorization> => {
    const { data } = await api.post<StorageAuthorization>(`/storage-sources/${sourceId}/authorize`, payload)
    return data
  },

  listWatchPaths: async (sourceId: string): Promise<StorageWatchPath[]> => {
    const { data } = await api.get<StorageWatchPathListResponse>(`/storage-sources/${sourceId}/watch-paths`)
    return data.items
  },

  createWatchPath: async (sourceId: string, payload: StorageWatchPathCreate): Promise<StorageWatchPath> => {
    const { data } = await api.post<StorageWatchPath>(`/storage-sources/${sourceId}/watch-paths`, payload)
    return data
  },
}

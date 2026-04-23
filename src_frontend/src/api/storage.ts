import api from './client'
import {
  StorageAuthorization,
  StorageAuthorizationCreatePayload,
  StorageAuthorizationListResponse,
  StorageHandshakeResult,
  StorageSource,
  StorageSourceCreatePayload,
  StorageSourceListResponse,
  StorageSourceUpdatePayload,
  StorageValidationResult,
  StorageWatchPath,
  StorageWatchPathCreatePayload,
  StorageWatchPathListResponse,
} from '@/types'

export const storageApi = {
  listStorageSources: async (projectId?: string): Promise<StorageSource[]> => {
    const { data } = await api.get<StorageSourceListResponse>('/storage-sources', {
      params: projectId ? { project_id: projectId } : undefined,
    })
    return data.storage_sources
  },

  createStorageSource: async (payload: StorageSourceCreatePayload): Promise<StorageSource> => {
    const { data } = await api.post<StorageSource>('/storage-sources', payload)
    return data
  },

  getStorageSource: async (sourceId: string): Promise<StorageSource> => {
    const { data } = await api.get<StorageSource>(`/storage-sources/${sourceId}`)
    return data
  },

  updateStorageSource: async (
    sourceId: string,
    payload: StorageSourceUpdatePayload,
  ): Promise<StorageSource> => {
    const { data } = await api.patch<StorageSource>(`/storage-sources/${sourceId}`, payload)
    return data
  },

  validateStorageSource: async (sourceId: string): Promise<StorageValidationResult> => {
    const { data } = await api.post<StorageValidationResult>(`/storage-sources/${sourceId}/validate`)
    return data
  },

  authorizeStorageSource: async (
    sourceId: string,
    payload: StorageAuthorizationCreatePayload,
  ): Promise<StorageAuthorization> => {
    const { data } = await api.post<StorageAuthorization>(
      `/storage-sources/${sourceId}/authorize`,
      payload,
    )
    return data
  },

  listAuthorizations: async (sourceId: string): Promise<StorageAuthorization[]> => {
    const { data } = await api.get<StorageAuthorizationListResponse>(
      `/storage-sources/${sourceId}/authorizations`,
    )
    return data.authorizations
  },

  listWatchPaths: async (sourceId: string): Promise<StorageWatchPath[]> => {
    const { data } = await api.get<StorageWatchPathListResponse>(
      `/storage-sources/${sourceId}/watch-paths`,
    )
    return data.watch_paths
  },

  createWatchPath: async (
    sourceId: string,
    payload: StorageWatchPathCreatePayload,
  ): Promise<StorageWatchPath> => {
    const { data } = await api.post<StorageWatchPath>(
      `/storage-sources/${sourceId}/watch-paths`,
      payload,
    )
    return data
  },

  getHandshake: async (sourceId: string): Promise<StorageHandshakeResult> => {
    const { data } = await api.get<StorageHandshakeResult>(`/storage-sources/${sourceId}/handshake`)
    return data
  },
}

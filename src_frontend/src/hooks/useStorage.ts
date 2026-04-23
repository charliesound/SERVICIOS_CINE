import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { storageApi } from '@/api'
import {
  StorageAuthorizationCreatePayload,
  StorageSourceCreatePayload,
  StorageSourceUpdatePayload,
  StorageWatchPathCreatePayload,
} from '@/types'

const storageKeys = {
  all: ['storageSources'] as const,
  list: (projectId?: string) => ['storageSources', projectId ?? 'all'] as const,
  detail: (sourceId: string) => ['storageSource', sourceId] as const,
  authorizations: (sourceId: string) => ['storageSource', sourceId, 'authorizations'] as const,
  watchPaths: (sourceId: string) => ['storageSource', sourceId, 'watchPaths'] as const,
  handshake: (sourceId: string) => ['storageSource', sourceId, 'handshake'] as const,
}

export function useStorageSources(projectId?: string) {
  return useQuery({
    queryKey: storageKeys.list(projectId),
    queryFn: () => storageApi.listStorageSources(projectId),
  })
}

export function useStorageSource(sourceId: string) {
  return useQuery({
    queryKey: storageKeys.detail(sourceId),
    queryFn: () => storageApi.getStorageSource(sourceId),
    enabled: !!sourceId,
  })
}

export function useStorageAuthorizations(sourceId: string) {
  return useQuery({
    queryKey: storageKeys.authorizations(sourceId),
    queryFn: () => storageApi.listAuthorizations(sourceId),
    enabled: !!sourceId,
  })
}

export function useStorageWatchPaths(sourceId: string) {
  return useQuery({
    queryKey: storageKeys.watchPaths(sourceId),
    queryFn: () => storageApi.listWatchPaths(sourceId),
    enabled: !!sourceId,
  })
}

export function useStorageHandshake(sourceId: string) {
  return useQuery({
    queryKey: storageKeys.handshake(sourceId),
    queryFn: () => storageApi.getHandshake(sourceId),
    enabled: !!sourceId,
  })
}

export function useCreateStorageSource() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: StorageSourceCreatePayload) => storageApi.createStorageSource(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: storageKeys.all })
    },
  })
}

export function useUpdateStorageSource(sourceId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: StorageSourceUpdatePayload) => storageApi.updateStorageSource(sourceId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: storageKeys.all })
      queryClient.invalidateQueries({ queryKey: storageKeys.detail(sourceId) })
      queryClient.invalidateQueries({ queryKey: storageKeys.handshake(sourceId) })
    },
  })
}

export function useValidateStorageSource(sourceId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => storageApi.validateStorageSource(sourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: storageKeys.handshake(sourceId) })
    },
  })
}

export function useAuthorizeStorageSource(sourceId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: StorageAuthorizationCreatePayload) =>
      storageApi.authorizeStorageSource(sourceId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: storageKeys.authorizations(sourceId) })
      queryClient.invalidateQueries({ queryKey: storageKeys.handshake(sourceId) })
    },
  })
}

export function useCreateWatchPath(sourceId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: StorageWatchPathCreatePayload) =>
      storageApi.createWatchPath(sourceId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: storageKeys.watchPaths(sourceId) })
    },
  })
}

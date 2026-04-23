import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { documentsApi } from '@/api'
import {
  DeriveReportRequest,
  DocumentApprovePayload,
  DocumentAssetCreatePayload,
  DocumentAssetUpdatePayload,
  DocumentListFilters,
} from '@/types'

const documentKeys = {
  list: (filters?: DocumentListFilters) => ['documents', filters ?? {}] as const,
  detail: (documentId: string) => ['document', documentId] as const,
  events: (documentId: string) => ['documentEvents', documentId] as const,
}

export function useDocuments(filters?: DocumentListFilters) {
  return useQuery({
    queryKey: documentKeys.list(filters),
    queryFn: () => documentsApi.listDocuments(filters),
  })
}

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: documentKeys.detail(documentId),
    queryFn: () => documentsApi.getDocument(documentId),
    enabled: !!documentId,
  })
}

export function useDocumentEvents(documentId: string) {
  return useQuery({
    queryKey: documentKeys.events(documentId),
    queryFn: () => documentsApi.getDocumentEvents(documentId),
    enabled: !!documentId,
  })
}

export function useCreateDocument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: DocumentAssetCreatePayload) => documentsApi.createDocument(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })
}

export function useUpdateDocument(documentId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: DocumentAssetUpdatePayload) => documentsApi.updateDocument(documentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(documentId) })
      queryClient.invalidateQueries({ queryKey: documentKeys.events(documentId) })
    },
  })
}

function createDocumentActionMutation(
  action: (documentId: string, payload?: DocumentApprovePayload) => Promise<unknown>,
  documentId: string,
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload?: DocumentApprovePayload) => action(documentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(documentId) })
      queryClient.invalidateQueries({ queryKey: documentKeys.events(documentId) })
    },
  })
}

export function useExtractDocument(documentId: string) {
  return createDocumentActionMutation((id) => documentsApi.extractDocument(id), documentId)
}

export function useClassifyDocument(documentId: string) {
  return createDocumentActionMutation((id) => documentsApi.classifyDocument(id), documentId)
}

export function useStructureDocument(documentId: string) {
  return createDocumentActionMutation((id) => documentsApi.structureDocument(id), documentId)
}

export function useApproveDocument(documentId: string) {
  return createDocumentActionMutation((id, payload) => documentsApi.approveDocument(id, payload), documentId)
}

export function useDeriveDocumentPreview(documentId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => documentsApi.deriveDocumentPreview(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(documentId) })
      queryClient.invalidateQueries({ queryKey: documentKeys.events(documentId) })
    },
  })
}

export function useDeriveDocumentReport(documentId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: DeriveReportRequest) => documentsApi.deriveDocumentReport(documentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(documentId) })
      queryClient.invalidateQueries({ queryKey: documentKeys.events(documentId) })
    },
  })
}

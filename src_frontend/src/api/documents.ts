import api from './client'
import {
  DerivePreviewResponse,
  DeriveReportRequest,
  DeriveReportResponse,
  DocumentApprovePayload,
  DocumentAsset,
  DocumentAssetCreatePayload,
  DocumentAssetListResponse,
  DocumentAssetUpdatePayload,
  DocumentEvent,
  DocumentEventListResponse,
  DocumentListFilters,
} from '@/types'

export const documentsApi = {
  listDocuments: async (filters?: DocumentListFilters): Promise<DocumentAsset[]> => {
    const { data } = await api.get<DocumentAssetListResponse>('/ingest/documents', { params: filters })
    return data.documents
  },

  createDocument: async (payload: DocumentAssetCreatePayload): Promise<DocumentAsset> => {
    const { data } = await api.post<DocumentAsset>('/ingest/documents', payload)
    return data
  },

  getDocument: async (documentId: string): Promise<DocumentAsset> => {
    const { data } = await api.get<DocumentAsset>(`/ingest/documents/${documentId}`)
    return data
  },

  updateDocument: async (
    documentId: string,
    payload: DocumentAssetUpdatePayload,
  ): Promise<DocumentAsset> => {
    const { data } = await api.patch<DocumentAsset>(`/ingest/documents/${documentId}`, payload)
    return data
  },

  extractDocument: async (documentId: string): Promise<DocumentAsset> => {
    const { data } = await api.post<DocumentAsset>(`/ingest/documents/${documentId}/extract`)
    return data
  },

  classifyDocument: async (documentId: string): Promise<DocumentAsset> => {
    const { data } = await api.post<DocumentAsset>(`/ingest/documents/${documentId}/classify`)
    return data
  },

  structureDocument: async (documentId: string): Promise<DocumentAsset> => {
    const { data } = await api.post<DocumentAsset>(`/ingest/documents/${documentId}/structure`)
    return data
  },

  approveDocument: async (
    documentId: string,
    payload?: DocumentApprovePayload,
  ): Promise<DocumentAsset> => {
    const { data } = await api.post<DocumentAsset>(`/ingest/documents/${documentId}/approve`, payload ?? {})
    return data
  },

  getDocumentEvents: async (documentId: string): Promise<DocumentEvent[]> => {
    const { data } = await api.get<DocumentEventListResponse>(`/ingest/documents/${documentId}/events`)
    return data.events
  },

  deriveDocumentPreview: async (documentId: string): Promise<DerivePreviewResponse> => {
    const { data } = await api.post<DerivePreviewResponse>(`/ingest/documents/${documentId}/derive-preview`)
    return data
  },

  deriveDocumentReport: async (documentId: string, payload: DeriveReportRequest): Promise<DeriveReportResponse> => {
    const { data } = await api.post<DeriveReportResponse>(`/ingest/documents/${documentId}/derive-report`, payload)
    return data
  },
}

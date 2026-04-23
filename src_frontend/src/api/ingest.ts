import api from './client'
import {
  IngestScan,
  IngestScanFilters,
  IngestScanLaunchPayload,
  IngestScanListResponse,
  MediaAsset,
  MediaAssetFilters,
  MediaAssetListResponse,
} from '@/types'

export const ingestApi = {
  launchStorageScan: async (
    sourceId: string,
    payload?: IngestScanLaunchPayload,
  ): Promise<IngestScan> => {
    const { data } = await api.post<IngestScan>(`/storage-sources/${sourceId}/scan`, payload ?? {})
    return data
  },

  listIngestScans: async (filters?: IngestScanFilters): Promise<IngestScan[]> => {
    const { data } = await api.get<IngestScanListResponse>('/ingest/scans', { params: filters })
    return data.scans
  },

  getIngestScan: async (scanId: string): Promise<IngestScan> => {
    const { data } = await api.get<IngestScan>(`/ingest/scans/${scanId}`)
    return data
  },

  listMediaAssets: async (filters?: MediaAssetFilters): Promise<MediaAsset[]> => {
    const { data } = await api.get<MediaAssetListResponse>('/ingest/assets', { params: filters })
    return data.assets
  },

  getMediaAsset: async (assetId: string): Promise<MediaAsset> => {
    const { data } = await api.get<MediaAsset>(`/ingest/assets/${assetId}`)
    return data
  },
}

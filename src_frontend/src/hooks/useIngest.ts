import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ingestApi } from '@/api'
import { IngestScanFilters, IngestScanLaunchPayload, MediaAssetFilters } from '@/types'

const ingestKeys = {
  scans: (filters?: IngestScanFilters) => ['ingestScans', filters ?? {}] as const,
  scan: (scanId: string) => ['ingestScan', scanId] as const,
  assets: (filters?: MediaAssetFilters) => ['mediaAssets', filters ?? {}] as const,
  asset: (assetId: string) => ['mediaAsset', assetId] as const,
}

export function useIngestScans(filters?: IngestScanFilters) {
  return useQuery({
    queryKey: ingestKeys.scans(filters),
    queryFn: () => ingestApi.listIngestScans(filters),
  })
}

export function useIngestScan(scanId: string) {
  return useQuery({
    queryKey: ingestKeys.scan(scanId),
    queryFn: () => ingestApi.getIngestScan(scanId),
    enabled: !!scanId,
  })
}

export function useMediaAssets(filters?: MediaAssetFilters) {
  return useQuery({
    queryKey: ingestKeys.assets(filters),
    queryFn: () => ingestApi.listMediaAssets(filters),
  })
}

export function useMediaAsset(assetId: string) {
  return useQuery({
    queryKey: ingestKeys.asset(assetId),
    queryFn: () => ingestApi.getMediaAsset(assetId),
    enabled: !!assetId,
  })
}

export function useLaunchStorageScan(sourceId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload?: IngestScanLaunchPayload) => ingestApi.launchStorageScan(sourceId, payload),
    onSuccess: (scan) => {
      queryClient.invalidateQueries({ queryKey: ['ingestScans'] })
      queryClient.invalidateQueries({ queryKey: ['mediaAssets'] })
      queryClient.invalidateQueries({ queryKey: ingestKeys.scan(scan.id) })
    },
  })
}

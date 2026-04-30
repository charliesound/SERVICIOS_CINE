import { useState, useEffect, useCallback } from 'react'
import { X, ChevronLeft, ChevronRight, Image, AlertCircle } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import type { ProjectImageAssetItem, ProjectImageAssetPaginationMeta } from '@/types/storyboard'

interface AssetPickerModalProps {
  isOpen: boolean
  projectId: string
  currentAssetId?: string
  onSelect: (assetId: string, previewUrl: string) => void
  onClose: () => void
}

export function AssetPickerModal({
  isOpen,
  projectId,
  currentAssetId,
  onSelect,
  onClose,
}: AssetPickerModalProps) {
  const [assets, setAssets] = useState<ProjectImageAssetItem[]>([])
  const [meta, setMeta] = useState<ProjectImageAssetPaginationMeta | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  const fetchAssets = useCallback(async (pageNum: number) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await storyboardApi.getImageAssets(projectId, pageNum, 20)
      setAssets(response.items)
      setMeta(response.meta)
      setPage(pageNum)
    } catch (err) {
      setError('Failed to load assets. Please try again.')
      console.error('Asset fetch error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    if (isOpen) {
      fetchAssets(1)
    }
  }, [isOpen, fetchAssets])

  const handleSelect = (asset: ProjectImageAssetItem) => {
    onSelect(asset.asset_id, asset.preview_url)
  }

  const handlePrevPage = () => {
    if (meta?.has_prev) {
      fetchAssets(page - 1)
    }
  }

  const handleNextPage = () => {
    if (meta?.has_next) {
      fetchAssets(page + 1)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      
      <div className="relative bg-dark-200 border border-white/10 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <h2 className="text-lg font-semibold text-white">Select Asset</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 min-h-[400px]">
          {isLoading && (
            <div className="flex items-center justify-center h-full">
              <div className="flex items-center gap-3 text-amber-400">
                <svg className="animate-spin w-6 h-6" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span className="text-sm">Loading assets...</span>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-full">
              <div className="flex flex-col items-center gap-3 text-red-400">
                <AlertCircle className="w-8 h-8" />
                <span>{error}</span>
                <button
                  onClick={() => fetchAssets(page)}
                  className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-sm transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          )}

          {!isLoading && !error && assets.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="flex flex-col items-center gap-3 text-gray-500">
                <Image className="w-12 h-12" />
                <span>No image assets found in this project</span>
              </div>
            </div>
          )}

          {!isLoading && !error && assets.length > 0 && (
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
              {assets.map((asset) => (
                <button
                  key={asset.asset_id}
                  onClick={() => handleSelect(asset)}
                  className={`group relative aspect-square rounded-lg overflow-hidden border-2 transition-all hover:scale-105 ${
                    asset.asset_id === currentAssetId
                      ? 'border-amber-500 ring-2 ring-amber-500/30'
                      : 'border-white/10 hover:border-white/30'
                  }`}
                >
                  <img
                    src={asset.thumbnail_url}
                    alt={asset.file_name}
                    loading="lazy"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="absolute bottom-0 left-0 right-0 p-2">
                      <p className="text-xs text-white truncate">{asset.file_name}</p>
                    </div>
                  </div>
                  {asset.asset_id === currentAssetId && (
                    <div className="absolute top-2 right-2 w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center">
                      <svg className="w-3 h-3 text-black" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {meta && meta.total_pages > 1 && (
          <div className="flex items-center justify-between p-4 border-t border-white/10">
            <span className="text-sm text-gray-400">
              Page {meta.page} of {meta.total_pages} ({meta.total_items} items)
            </span>
            <div className="flex gap-2">
              <button
                onClick={handlePrevPage}
                disabled={!meta.has_prev}
                className={`p-2 rounded-lg transition-colors ${
                  meta.has_prev
                    ? 'bg-white/10 hover:bg-white/20 text-white'
                    : 'bg-white/5 text-gray-600 cursor-not-allowed'
                }`}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={handleNextPage}
                disabled={!meta.has_next}
                className={`p-2 rounded-lg transition-colors ${
                  meta.has_next
                    ? 'bg-white/10 hover:bg-white/20 text-white'
                    : 'bg-white/5 text-gray-600 cursor-not-allowed'
                }`}
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

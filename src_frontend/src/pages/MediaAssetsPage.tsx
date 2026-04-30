import { useMemo } from 'react'
import axios from 'axios'
import { Link, useSearchParams } from 'react-router-dom'
import { FileSearch, RefreshCw } from 'lucide-react'
import StorageStatusBadge from '@/components/StorageStatusBadge'
import { useMediaAssets } from '@/hooks'

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
  }
  return fallback
}

function formatBytes(value: number) {
  if (!value) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const exponent = Math.min(Math.floor(Math.log(value) / Math.log(1024)), units.length - 1)
  const size = value / 1024 ** exponent
  return `${size.toFixed(exponent === 0 ? 0 : 2)} ${units[exponent]}`
}

export default function MediaAssetsPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters = useMemo(() => {
    const sourceId = searchParams.get('source_id')?.trim() || undefined
    const status = searchParams.get('status')?.trim() || undefined
    const assetType = searchParams.get('asset_type')?.trim() || undefined
    return { source_id: sourceId, status, asset_type: assetType }
  }, [searchParams])

  const assetsQuery = useMediaAssets(filters)

  const applyFilter = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams)
    if (value.trim()) next.set(key, value.trim())
    else next.delete(key)
    setSearchParams(next)
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="heading-lg flex items-center gap-3">
            <FileSearch className="h-6 w-6 text-amber-400" />
            Media Indexada
          </h1>
          <p className="mt-1 text-slate-400">Archivos indexados de rutas existentes. Son referencias, no copias. CID no mueve ni renombra.</p>
        </div>

        <div className="flex gap-3">
          <Link to="/ingest/scans" className="btn-secondary">View Scans</Link>
          <button className="btn-secondary flex items-center gap-2" onClick={() => assetsQuery.refetch()}>
            <RefreshCw className={`h-4 w-4 ${assetsQuery.isFetching ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <section className="card card-hover">
        <div className="grid gap-4 lg:grid-cols-3">
          <div>
            <label className="label" htmlFor="asset_source_id">Source ID</label>
            <input
              id="asset_source_id"
              className="input"
              defaultValue={filters.source_id ?? ''}
              onBlur={(event) => applyFilter('source_id', event.target.value)}
              placeholder="Filter by storage source"
            />
          </div>
          <div>
            <label className="label" htmlFor="asset_status">Status</label>
            <select
              id="asset_status"
              className="input"
              value={filters.status ?? ''}
              onChange={(event) => applyFilter('status', event.target.value)}
            >
              <option value="">All statuses</option>
              <option value="indexed">indexed</option>
            </select>
          </div>
          <div>
            <label className="label" htmlFor="asset_type">Asset Type</label>
            <select
              id="asset_type"
              className="input"
              value={filters.asset_type ?? ''}
              onChange={(event) => applyFilter('asset_type', event.target.value)}
            >
              <option value="">All asset types</option>
              <option value="video">video</option>
              <option value="audio">audio</option>
              <option value="image">image</option>
              <option value="document">document</option>
              <option value="other">other</option>
            </select>
          </div>
        </div>
      </section>

      <section className="card card-hover space-y-4">
        {assetsQuery.error && (
          <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {getErrorMessage(assetsQuery.error, 'Unable to load media assets')}
          </div>
        )}

        {assetsQuery.isLoading && <div className="text-sm text-slate-400">Loading media assets...</div>}

        {!assetsQuery.isLoading && !assetsQuery.error && (!assetsQuery.data || assetsQuery.data.length === 0) && (
          <div className="rounded-xl border border-dashed border-white/10 px-6 py-10 text-center text-sm text-slate-400">
            No media assets found for the current filters.
          </div>
        )}

        {assetsQuery.data?.map((asset) => (
          <article key={asset.id} className="rounded-2xl border border-white/10 bg-dark-300/40 p-5">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
              <div className="space-y-3 min-w-0">
                <div className="flex flex-wrap items-center gap-3">
                  <h2 className="text-lg font-semibold text-white break-all">{asset.file_name}</h2>
                  <StorageStatusBadge status={asset.status} />
                  <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-2.5 py-1 text-xs font-medium uppercase tracking-wide text-blue-300">
                    {asset.asset_type}
                  </span>
                </div>
                <div className="grid gap-2 text-sm text-slate-300 md:grid-cols-2">
                  <p><span className="text-slate-500">Extension:</span> {asset.file_extension || 'n/a'}</p>
                  <p><span className="text-slate-500">MIME:</span> {asset.mime_type || 'n/a'}</p>
                  <p><span className="text-slate-500">Size:</span> {formatBytes(asset.file_size)}</p>
                  <p><span className="text-slate-500">Status:</span> {asset.status}</p>
                  <p><span className="text-slate-500">Source:</span> {asset.storage_source_id}</p>
                  <p><span className="text-slate-500">Scan:</span> {asset.ingest_scan_id || 'n/a'}</p>
                </div>
                <p className="text-sm text-slate-400 break-all">{asset.relative_path}</p>
              </div>

              <Link to={`/ingest/assets/${asset.id}`} className="btn-secondary">
                Open Detail
              </Link>
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}

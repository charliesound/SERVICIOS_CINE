import axios from 'axios'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, FileSearch } from 'lucide-react'
import StorageStatusBadge from '@/components/StorageStatusBadge'
import { useMediaAsset } from '@/hooks'

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

export default function MediaAssetDetailPage() {
  const { assetId = '' } = useParams()
  const assetQuery = useMediaAsset(assetId)

  if (!assetId) {
    return <div className="card text-sm text-red-200">Missing media asset id.</div>
  }

  if (assetQuery.isLoading) {
    return <div className="text-sm text-slate-400">Loading media asset...</div>
  }

  if (assetQuery.error || !assetQuery.data) {
    return (
      <div className="card space-y-4">
        <Link to="/ingest/assets" className="btn-ghost inline-flex items-center gap-2 px-0">
          <ArrowLeft className="h-4 w-4" />
          Back to assets
        </Link>
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {getErrorMessage(assetQuery.error, 'Media asset not found')}
        </div>
      </div>
    )
  }

  const asset = assetQuery.data

  return (
    <div className="space-y-8">
      <div>
        <Link to="/ingest/assets" className="btn-ghost inline-flex items-center gap-2 px-0">
          <ArrowLeft className="h-4 w-4" />
          Back to assets
        </Link>
        <h1 className="heading-lg mt-2 flex items-center gap-3">
          <FileSearch className="h-6 w-6 text-amber-400" />
          Media Asset Detail
        </h1>
      </div>

      <section className="card card-hover space-y-6">
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="text-lg font-semibold text-white break-all">{asset.file_name}</h2>
          <StorageStatusBadge status={asset.status} />
          <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-2.5 py-1 text-xs font-medium uppercase tracking-wide text-blue-300">
            {asset.asset_type}
          </span>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Asset ID</p>
            <p className="mt-2 text-sm text-white break-all">{asset.id}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Storage Source ID</p>
            <p className="mt-2 text-sm text-white break-all">{asset.storage_source_id}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">ID de Escaneo</p>
            <p className="mt-2 text-sm text-white break-all">{asset.ingest_scan_id || 'n/a'}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Watch Path ID</p>
            <p className="mt-2 text-sm text-white break-all">{asset.watch_path_id || 'n/a'}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Extension</p>
            <p className="mt-2 text-sm text-white">{asset.file_extension || 'n/a'}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">MIME Type</p>
            <p className="mt-2 text-sm text-white">{asset.mime_type || 'n/a'}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">File Size</p>
            <p className="mt-2 text-sm text-white">{formatBytes(asset.file_size)}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Discovered At</p>
            <p className="mt-2 text-sm text-white">{new Date(asset.discovered_at).toLocaleString()}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Modified At</p>
            <p className="mt-2 text-sm text-white">{asset.modified_at ? new Date(asset.modified_at).toLocaleString() : 'n/a'}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Status</p>
            <p className="mt-2 text-sm text-white">{asset.status}</p>
          </div>
        </div>

        <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4 space-y-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Relative Path</p>
            <p className="mt-2 text-sm text-white break-all">{asset.relative_path}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Canonical Path</p>
            <p className="mt-2 text-sm text-white break-all">{asset.canonical_path}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link to={`/storage-sources/${asset.storage_source_id}`} className="btn-secondary">
            Open Storage Source
          </Link>
          <Link to={`/documents?media_asset_id=${encodeURIComponent(asset.id)}`} className="btn-secondary">
            Register as Document
          </Link>
          {asset.ingest_scan_id && (
            <Link to={`/ingest/scans/${asset.ingest_scan_id}`} className="btn-secondary">
              Abrir Escaneo
            </Link>
          )}
        </div>
      </section>
    </div>
  )
}

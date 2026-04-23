import axios from 'axios'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Search } from 'lucide-react'
import StorageStatusBadge from '@/components/StorageStatusBadge'
import { useIngestScan } from '@/hooks'

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
  }
  return fallback
}

export default function IngestScanDetailPage() {
  const { scanId = '' } = useParams()
  const scanQuery = useIngestScan(scanId)

  if (!scanId) {
    return <div className="card text-sm text-red-200">Missing ingest scan id.</div>
  }

  if (scanQuery.isLoading) {
    return <div className="text-sm text-slate-400">Loading ingest scan...</div>
  }

  if (scanQuery.error || !scanQuery.data) {
    return (
      <div className="card space-y-4">
        <Link to="/ingest/scans" className="btn-ghost inline-flex items-center gap-2 px-0">
          <ArrowLeft className="h-4 w-4" />
          Back to scans
        </Link>
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {getErrorMessage(scanQuery.error, 'Ingest scan not found')}
        </div>
      </div>
    )
  }

  const scan = scanQuery.data

  return (
    <div className="space-y-8">
      <div>
        <Link to="/ingest/scans" className="btn-ghost inline-flex items-center gap-2 px-0">
          <ArrowLeft className="h-4 w-4" />
          Back to scans
        </Link>
        <h1 className="heading-lg mt-2 flex items-center gap-3">
          <Search className="h-6 w-6 text-amber-400" />
          Scan Detail
        </h1>
      </div>

      <section className="card card-hover space-y-6">
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="text-lg font-semibold text-white break-all">{scan.id}</h2>
          <StorageStatusBadge status={scan.status} />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Storage Source</p>
            <p className="mt-2 text-sm text-white break-all">{scan.storage_source_id}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Watch Path</p>
            <p className="mt-2 text-sm text-white break-all">{scan.watch_path_id || 'All eligible watch paths'}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Started At</p>
            <p className="mt-2 text-sm text-white">{new Date(scan.started_at).toLocaleString()}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Finished At</p>
            <p className="mt-2 text-sm text-white">{scan.finished_at ? new Date(scan.finished_at).toLocaleString() : 'In progress'}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Files Discovered</p>
            <p className="mt-2 text-2xl font-semibold text-white">{scan.files_discovered_count}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Files Indexed</p>
            <p className="mt-2 text-2xl font-semibold text-white">{scan.files_indexed_count}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Files Skipped</p>
            <p className="mt-2 text-2xl font-semibold text-white">{scan.files_skipped_count}</p>
          </div>
          <div className="rounded-xl bg-dark-300/50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Created By</p>
            <p className="mt-2 text-sm text-white">{scan.created_by || 'System'}</p>
          </div>
        </div>

        <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Error Message</p>
          <p className="mt-2 text-sm text-white">{scan.error_message || 'None'}</p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link to={`/storage-sources/${scan.storage_source_id}`} className="btn-secondary">
            Open Storage Source
          </Link>
          <Link to={`/ingest/assets?source_id=${encodeURIComponent(scan.storage_source_id)}`} className="btn-secondary">
            Browse Related Assets
          </Link>
        </div>
      </section>
    </div>
  )
}

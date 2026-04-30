import { useMemo } from 'react'
import axios from 'axios'
import { Link, useSearchParams } from 'react-router-dom'
import { RefreshCw, Search } from 'lucide-react'
import StorageStatusBadge from '@/components/StorageStatusBadge'
import { useIngestScans } from '@/hooks'

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map((item) => (typeof item?.msg === 'string' ? item.msg : JSON.stringify(item))).join(', ')
    }
  }
  return fallback
}

export default function IngestScansPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters = useMemo(() => {
    const sourceId = searchParams.get('source_id')?.trim() || undefined
    const status = searchParams.get('status')?.trim() || undefined
    return { source_id: sourceId, status }
  }, [searchParams])

  const scansQuery = useIngestScans(filters)

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
            <Search className="h-6 w-6 text-amber-400" />
            Media Scans
          </h1>
          <p className="mt-1 text-slate-400">Escaneo de carpetas con media existente. CID lee y indexa, no mueve ni copia archivos.</p>
        </div>

        <div className="flex gap-3">
          <Link to="/ingest/assets" className="btn-secondary">View Assets</Link>
          <button className="btn-secondary flex items-center gap-2" onClick={() => scansQuery.refetch()}>
            <RefreshCw className={`h-4 w-4 ${scansQuery.isFetching ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <section className="card card-hover">
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="label" htmlFor="scan_source_id">Source ID</label>
            <input
              id="scan_source_id"
              className="input"
              defaultValue={filters.source_id ?? ''}
              onBlur={(event) => applyFilter('source_id', event.target.value)}
              placeholder="Filter by storage source"
            />
          </div>
          <div>
            <label className="label" htmlFor="scan_status">Status</label>
            <select
              id="scan_status"
              className="input"
              value={filters.status ?? ''}
              onChange={(event) => applyFilter('status', event.target.value)}
            >
              <option value="">All statuses</option>
              <option value="running">running</option>
              <option value="completed">completed</option>
              <option value="failed">failed</option>
            </select>
          </div>
        </div>
      </section>

      <section className="card card-hover space-y-4">
        {scansQuery.error && (
          <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {getErrorMessage(scansQuery.error, 'Unable to load ingest scans')}
          </div>
        )}

        {scansQuery.isLoading && <div className="text-sm text-slate-400">Loading media scans...</div>}

        {!scansQuery.isLoading && !scansQuery.error && (!scansQuery.data || scansQuery.data.length === 0) && (
          <div className="rounded-xl border border-dashed border-white/10 px-6 py-10 text-center text-sm text-slate-400">
            No scans found for the current filters.
          </div>
        )}

        {scansQuery.data?.map((scan) => (
          <article key={scan.id} className="rounded-2xl border border-white/10 bg-dark-300/40 p-5">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
              <div className="space-y-3">
                <div className="flex flex-wrap items-center gap-3">
                  <h2 className="text-lg font-semibold text-white">{scan.id}</h2>
                  <StorageStatusBadge status={scan.status} />
                </div>
                <div className="grid gap-2 text-sm text-slate-300 md:grid-cols-2">
                  <p><span className="text-slate-500">Source:</span> {scan.storage_source_id}</p>
                  <p><span className="text-slate-500">Watch Path:</span> {scan.watch_path_id || 'All eligible paths'}</p>
                  <p><span className="text-slate-500">Started:</span> {new Date(scan.started_at).toLocaleString()}</p>
                  <p><span className="text-slate-500">Finished:</span> {scan.finished_at ? new Date(scan.finished_at).toLocaleString() : 'In progress'}</p>
                  <p><span className="text-slate-500">Discovered:</span> {scan.files_discovered_count}</p>
                  <p><span className="text-slate-500">Indexed:</span> {scan.files_indexed_count}</p>
                  <p><span className="text-slate-500">Skipped:</span> {scan.files_skipped_count}</p>
                  <p><span className="text-slate-500">Error:</span> {scan.error_message || 'None'}</p>
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <Link to={`/ingest/assets?source_id=${encodeURIComponent(scan.storage_source_id)}`} className="btn-secondary">
                  View Assets
                </Link>
                <Link to={`/ingest/scans/${scan.id}`} className="btn-secondary">
                  Open Detail
                </Link>
              </div>
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}

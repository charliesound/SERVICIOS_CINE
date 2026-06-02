import { useMemo } from 'react'
import axios from 'axios'
import { Link, useSearchParams } from 'react-router-dom'
import { RefreshCw, Search } from 'lucide-react'
import { useLanguage } from '@/i18n'
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
  const { t } = useLanguage()
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
            {t('internal.ingestScansPage.title')}
          </h1>
          <p className="mt-1 text-slate-400">{t('internal.ingestScansPage.description')}</p>
        </div>

        <div className="flex gap-3">
          <Link to="/ingest/assets" className="btn-secondary">{t('internal.ingestScansPage.viewAssets')}</Link>
          <button className="btn-secondary flex items-center gap-2" onClick={() => scansQuery.refetch()}>
            <RefreshCw className={`h-4 w-4 ${scansQuery.isFetching ? 'animate-spin' : ''}`} />
            {t('internal.ingestScansPage.refresh')}
          </button>
        </div>
      </div>

      <section className="card card-hover">
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="label" htmlFor="scan_source_id">{t('internal.ingestScansPage.filterSourceId')}</label>
            <input
              id="scan_source_id"
              className="input"
              defaultValue={filters.source_id ?? ''}
              onBlur={(event) => applyFilter('source_id', event.target.value)}
              placeholder={t('internal.ingestScansPage.filterSourcePlaceholder')}
            />
          </div>
          <div>
            <label className="label" htmlFor="scan_status">{t('internal.ingestScansPage.filterStatus')}</label>
            <select
              id="scan_status"
              className="input"
              value={filters.status ?? ''}
              onChange={(event) => applyFilter('status', event.target.value)}
            >
              <option value="">{t('internal.ingestScansPage.filterStatusAll')}</option>
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
            {getErrorMessage(scansQuery.error, t('internal.ingestScansPage.loadError'))}
          </div>
        )}

        {scansQuery.isLoading && <div className="text-sm text-slate-400">{t('internal.ingestScansPage.loading')}</div>}

        {!scansQuery.isLoading && !scansQuery.error && (!scansQuery.data || scansQuery.data.length === 0) && (
          <div className="rounded-xl border border-dashed border-white/10 px-6 py-10 text-center text-sm text-slate-400">
            {t('internal.ingestScansPage.empty')}
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
                  <p><span className="text-slate-500">{t('internal.ingestScansPage.fieldSource')}</span> {scan.storage_source_id}</p>
                  <p><span className="text-slate-500">{t('internal.ingestScansPage.fieldWatchPath')}</span> {scan.watch_path_id || t('internal.ingestScansPage.allEligiblePaths')}</p>
                  <p><span className="text-slate-500">{t('internal.ingestScansPage.fieldStarted')}</span> {new Date(scan.started_at).toLocaleString()}</p>
                  <p><span className="text-slate-500">{t('internal.ingestScansPage.fieldFinished')}</span> {scan.finished_at ? new Date(scan.finished_at).toLocaleString() : t('internal.ingestScansPage.fieldInProgress')}</p>
                  <p><span className="text-slate-500">{t('internal.ingestScansPage.fieldDiscovered')}</span> {scan.files_discovered_count}</p>
                  <p><span className="text-slate-500">{t('internal.ingestScansPage.fieldIndexed')}</span> {scan.files_indexed_count}</p>
                  <p><span className="text-slate-500">{t('internal.ingestScansPage.fieldSkipped')}</span> {scan.files_skipped_count}</p>
                  <p><span className="text-slate-500">{t('internal.ingestScansPage.fieldError')}</span> {scan.error_message || t('internal.ingestScansPage.none')}</p>
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <Link to={`/ingest/assets?source_id=${encodeURIComponent(scan.storage_source_id)}`} className="btn-secondary">
                  {t('internal.ingestScansPage.viewAssetsAction')}
                </Link>
                <Link to={`/ingest/scans/${scan.id}`} className="btn-secondary">
                  {t('internal.ingestScansPage.openDetail')}
                </Link>
              </div>
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}

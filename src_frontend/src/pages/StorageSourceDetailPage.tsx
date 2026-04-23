import { useMemo, useState } from 'react'
import axios from 'axios'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  CheckCircle2,
  FolderTree,
  HardDrive,
  RefreshCw,
  Search,
  ShieldCheck,
} from 'lucide-react'
import StorageAuthorizationForm from '@/components/StorageAuthorizationForm'
import StorageSourceForm from '@/components/StorageSourceForm'
import StorageStatusBadge from '@/components/StorageStatusBadge'
import WatchPathForm from '@/components/WatchPathForm'
import {
  useAuthorizeStorageSource,
  useCreateWatchPath,
  useLaunchStorageScan,
  useStorageAuthorizations,
  useStorageHandshake,
  useStorageSource,
  useStorageWatchPaths,
  useUpdateStorageSource,
  useValidateStorageSource,
} from '@/hooks'
import {
  StorageAuthorizationCreatePayload,
  StorageSourceUpdatePayload,
  StorageValidationResult,
  StorageWatchPathCreatePayload,
} from '@/types'

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail
        .map((item) => (typeof item?.msg === 'string' ? item.msg : JSON.stringify(item)))
        .join(', ')
    }
  }
  return fallback
}

function formatBytes(value?: number | null) {
  if (value == null || Number.isNaN(value)) return 'n/a'
  if (value === 0) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const exponent = Math.min(Math.floor(Math.log(value) / Math.log(1024)), units.length - 1)
  const size = value / 1024 ** exponent
  return `${size.toFixed(exponent === 0 ? 0 : 2)} ${units[exponent]}`
}

export default function StorageSourceDetailPage() {
  const { sourceId = '' } = useParams()
  const [actionError, setActionError] = useState<string | null>(null)
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)
  const [validationResult, setValidationResult] = useState<StorageValidationResult | null>(null)

  const sourceQuery = useStorageSource(sourceId)
  const authorizationsQuery = useStorageAuthorizations(sourceId)
  const watchPathsQuery = useStorageWatchPaths(sourceId)
  const handshakeQuery = useStorageHandshake(sourceId)

  const updateSource = useUpdateStorageSource(sourceId)
  const validateSource = useValidateStorageSource(sourceId)
  const authorizeSource = useAuthorizeStorageSource(sourceId)
  const createWatchPath = useCreateWatchPath(sourceId)
  const launchScan = useLaunchStorageScan(sourceId)

  const metadata = useMemo(() => {
    return validationResult?.metadata ?? handshakeQuery.data?.metadata
  }, [handshakeQuery.data?.metadata, validationResult])

  const clearMessages = () => {
    setActionError(null)
    setActionSuccess(null)
  }

  const handleUpdate = async (payload: StorageSourceUpdatePayload) => {
    clearMessages()

    try {
      await updateSource.mutateAsync(payload)
      setActionSuccess('Storage source updated')
    } catch (error) {
      setActionError(getErrorMessage(error, 'Unable to update storage source'))
    }
  }

  const handleValidate = async () => {
    clearMessages()

    try {
      const result = await validateSource.mutateAsync()
      setValidationResult(result)
      setActionSuccess('Storage source validated')
      handshakeQuery.refetch()
    } catch (error) {
      setActionError(getErrorMessage(error, 'Unable to validate storage source'))
    }
  }

  const handleAuthorize = async (payload: StorageAuthorizationCreatePayload) => {
    clearMessages()

    try {
      await authorizeSource.mutateAsync(payload)
      setActionSuccess('Authorization created')
    } catch (error) {
      setActionError(getErrorMessage(error, 'Unable to authorize storage source'))
    }
  }

  const handleWatchPath = async (payload: StorageWatchPathCreatePayload) => {
    clearMessages()

    try {
      await createWatchPath.mutateAsync(payload)
      setActionSuccess('Watch path added')
    } catch (error) {
      setActionError(getErrorMessage(error, 'Unable to create watch path'))
    }
  }

  const handleLaunchScan = async () => {
    clearMessages()

    try {
      const scan = await launchScan.mutateAsync({})
      setActionSuccess(`Scan launched: ${scan.id}`)
    } catch (error) {
      setActionError(getErrorMessage(error, 'Unable to launch scan'))
    }
  }

  if (!sourceId) {
    return (
      <div className="card">
        <p className="text-sm text-red-200">Missing storage source id.</p>
      </div>
    )
  }

  if (sourceQuery.isLoading) {
    return <div className="text-sm text-slate-400">Loading storage source...</div>
  }

  if (sourceQuery.error || !sourceQuery.data) {
    return (
      <div className="card space-y-4">
        <Link to="/storage-sources" className="btn-ghost inline-flex items-center gap-2 px-0">
          <ArrowLeft className="h-4 w-4" />
          Back to storage sources
        </Link>
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {getErrorMessage(sourceQuery.error, 'Storage source not found')}
        </div>
      </div>
    )
  }

  const source = sourceQuery.data
  const handshakeError = handshakeQuery.error
    ? getErrorMessage(handshakeQuery.error, 'Unable to run handshake')
    : null

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <Link to="/storage-sources" className="btn-ghost inline-flex items-center gap-2 px-0">
            <ArrowLeft className="h-4 w-4" />
            Back to storage sources
          </Link>
          <h1 className="heading-lg mt-2 flex items-center gap-3">
            <HardDrive className="h-6 w-6 text-amber-400" />
            {source.name}
          </h1>
          <p className="mt-1 text-slate-400">{source.mount_path}</p>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            className="btn-secondary flex items-center gap-2"
            onClick={handleLaunchScan}
            disabled={launchScan.isPending}
          >
            <Search className="h-4 w-4" />
            {launchScan.isPending ? 'Launching Scan...' : 'Launch Scan'}
          </button>
          <button
            className="btn-secondary flex items-center gap-2"
            onClick={() => handshakeQuery.refetch()}
            disabled={handshakeQuery.isFetching}
          >
            <RefreshCw className={`h-4 w-4 ${handshakeQuery.isFetching ? 'animate-spin' : ''}`} />
            Refresh Handshake
          </button>
          <button
            className="btn-primary flex items-center gap-2"
            onClick={handleValidate}
            disabled={validateSource.isPending}
          >
            <CheckCircle2 className="h-4 w-4" />
            {validateSource.isPending ? 'Validating...' : 'Validate Source'}
          </button>
        </div>
      </div>

      {actionError && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {actionError}
        </div>
      )}

      {actionSuccess && (
        <div className="rounded-xl border border-green-500/20 bg-green-500/10 px-4 py-3 text-sm text-green-200">
          {actionSuccess}
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[1.1fr,1.4fr]">
        <div className="space-y-6">
          <section className="card card-hover space-y-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="heading-md">Source Overview</h2>
              <StorageStatusBadge status={source.status} />
            </div>

            <div className="grid gap-3 text-sm text-slate-300">
              <p><span className="text-slate-500">Source Type:</span> {source.source_type}</p>
              <p><span className="text-slate-500">Organization ID:</span> {source.organization_id}</p>
              <p><span className="text-slate-500">Project ID:</span> {source.project_id}</p>
              <p><span className="text-slate-500">Created At:</span> {new Date(source.created_at).toLocaleString()}</p>
              <p><span className="text-slate-500">Updated At:</span> {new Date(source.updated_at).toLocaleString()}</p>
            </div>

            <div className="flex flex-wrap gap-3 pt-2">
              <Link to={`/ingest/scans?source_id=${encodeURIComponent(source.id)}`} className="btn-secondary">
                View Related Scans
              </Link>
              <Link to={`/ingest/assets?source_id=${encodeURIComponent(source.id)}`} className="btn-secondary">
                View Related Assets
              </Link>
            </div>
          </section>

          <section className="card card-hover">
            <h2 className="heading-md mb-5">Edit Source</h2>
            <StorageSourceForm
              mode="edit"
              initialValues={source}
              submitLabel="Save Changes"
              isSubmitting={updateSource.isPending}
              onSubmit={handleUpdate}
            />
          </section>

          <section className="card card-hover">
            <div className="mb-5 flex items-center gap-3">
              <ShieldCheck className="h-5 w-5 text-amber-400" />
              <h2 className="heading-md">Authorize Source</h2>
            </div>
            <StorageAuthorizationForm
              isSubmitting={authorizeSource.isPending}
              onSubmit={handleAuthorize}
            />
          </section>

          <section className="card card-hover">
            <div className="mb-5 flex items-center gap-3">
              <FolderTree className="h-5 w-5 text-amber-400" />
              <h2 className="heading-md">Watch Paths</h2>
            </div>
            <WatchPathForm
              isSubmitting={createWatchPath.isPending}
              onSubmit={handleWatchPath}
            />
          </section>
        </div>

        <div className="space-y-6">
          <section className="card card-hover">
            <div className="mb-5 flex items-center justify-between gap-3">
              <div>
                <h2 className="heading-md">Handshake Result</h2>
                <p className="text-sm text-slate-400">Current validation snapshot for this mount.</p>
              </div>
              {handshakeQuery.data && (
                <StorageStatusBadge status={handshakeQuery.data.validated ? 'active' : 'error'} />
              )}
            </div>

            {handshakeError && (
              <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {handshakeError}
              </div>
            )}

            {handshakeQuery.isLoading && <div className="text-sm text-slate-400">Running handshake...</div>}

            {metadata && (
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-xl bg-dark-300/50 p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Exists</p>
                  <p className="mt-2 text-lg font-semibold text-white">{metadata.exists ? 'Yes' : 'No'}</p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Directory</p>
                  <p className="mt-2 text-lg font-semibold text-white">{metadata.is_dir ? 'Yes' : 'No'}</p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Readable</p>
                  <p className="mt-2 text-lg font-semibold text-white">{metadata.readable ? 'Yes' : 'No'}</p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Writable</p>
                  <p className="mt-2 text-lg font-semibold text-white">
                    {metadata.writable == null ? 'n/a' : metadata.writable ? 'Yes' : 'No'}
                  </p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Free Space</p>
                  <p className="mt-2 text-lg font-semibold text-white">{formatBytes(metadata.free_space)}</p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Total Space</p>
                  <p className="mt-2 text-lg font-semibold text-white">{formatBytes(metadata.total_space)}</p>
                </div>
              </div>
            )}

            {metadata?.normalized_path && (
              <p className="mt-4 text-sm text-slate-400">
                <span className="text-slate-500">Normalized path:</span> {metadata.normalized_path}
              </p>
            )}
          </section>

          <section className="card card-hover">
            <div className="mb-5 flex items-center justify-between gap-3">
              <div>
                <h2 className="heading-md">Authorizations</h2>
                <p className="text-sm text-slate-400">Current scopes granted to this source.</p>
              </div>
              <span className="rounded-full bg-white/5 px-3 py-1 text-xs font-medium text-slate-300">
                {authorizationsQuery.data?.length ?? 0}
              </span>
            </div>

            {authorizationsQuery.error && (
              <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {getErrorMessage(authorizationsQuery.error, 'Unable to load authorizations')}
              </div>
            )}

            <div className="space-y-3">
              {authorizationsQuery.data?.map((authorization) => (
                <div key={authorization.id} className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="font-medium text-white">{authorization.scope_path}</p>
                      <p className="mt-1 text-sm text-slate-400">
                        Mode: {authorization.authorization_mode} · Granted {new Date(authorization.granted_at).toLocaleString()}
                      </p>
                    </div>
                    <StorageStatusBadge status={authorization.status} />
                  </div>
                </div>
              ))}

              {!authorizationsQuery.isLoading && (!authorizationsQuery.data || authorizationsQuery.data.length === 0) && (
                <p className="text-sm text-slate-400">No authorizations registered for this source.</p>
              )}
            </div>
          </section>

          <section className="card card-hover">
            <div className="mb-5 flex items-center justify-between gap-3">
              <div>
                <h2 className="heading-md">Watch Path List</h2>
                <p className="text-sm text-slate-400">Folders observed for future ingest workflows.</p>
              </div>
              <span className="rounded-full bg-white/5 px-3 py-1 text-xs font-medium text-slate-300">
                {watchPathsQuery.data?.length ?? 0}
              </span>
            </div>

            {watchPathsQuery.error && (
              <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {getErrorMessage(watchPathsQuery.error, 'Unable to load watch paths')}
              </div>
            )}

            <div className="space-y-3">
              {watchPathsQuery.data?.map((watchPath) => (
                <div key={watchPath.id} className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="font-medium text-white">{watchPath.watch_path}</p>
                      <p className="mt-1 text-sm text-slate-400">
                        Created {new Date(watchPath.created_at).toLocaleString()}
                        {watchPath.last_validated_at
                          ? ` · Last validated ${new Date(watchPath.last_validated_at).toLocaleString()}`
                          : ''}
                      </p>
                    </div>
                    <StorageStatusBadge status={watchPath.status} />
                  </div>
                </div>
              ))}

              {!watchPathsQuery.isLoading && (!watchPathsQuery.data || watchPathsQuery.data.length === 0) && (
                <p className="text-sm text-slate-400">No watch paths configured yet.</p>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

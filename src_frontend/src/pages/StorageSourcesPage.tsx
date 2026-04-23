import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { Link, useNavigate } from 'react-router-dom'
import { Database, FolderOpen, HardDrive, RefreshCw } from 'lucide-react'
import api from '@/api/client'
import StorageSourceForm from '@/components/StorageSourceForm'
import StorageStatusBadge from '@/components/StorageStatusBadge'
import { useCreateStorageSource, useStorageSources } from '@/hooks'
import { StorageSourceCreatePayload } from '@/types'

interface ProjectOption {
  id: string
  organization_id: string
  name: string
  description?: string | null
  status: string
}

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

export default function StorageSourcesPage() {
  const navigate = useNavigate()
  const { data: sources, isLoading, error, refetch, isFetching } = useStorageSources()
  const createSource = useCreateStorageSource()
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [projectOptions, setProjectOptions] = useState<ProjectOption[]>([])
  const [projectsLoading, setProjectsLoading] = useState(true)
  const [projectsError, setProjectsError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    const loadProjects = async () => {
      setProjectsLoading(true)
      setProjectsError(null)

      try {
        const { data } = await api.get<{ projects: ProjectOption[] }>('/projects')
        if (!active) return
        setProjectOptions(data.projects ?? [])
      } catch (projectError) {
        if (!active) return
        setProjectsError(getErrorMessage(projectError, 'Unable to load project defaults'))
      } finally {
        if (active) setProjectsLoading(false)
      }
    }

    loadProjects()

    return () => {
      active = false
    }
  }, [])

  const defaultProject = useMemo(() => projectOptions[0] ?? null, [projectOptions])
  const defaultFormValues = useMemo(
    () =>
      defaultProject
        ? {
            organization_id: defaultProject.organization_id,
            project_id: defaultProject.id,
            name: 'Demo Ingest Source',
            source_type: 'local',
            mount_path: '/home/harliesound/demo_ingest',
          }
        : undefined,
    [defaultProject],
  )

  const handleCreateSource = async (payload: StorageSourceCreatePayload) => {
    setSubmitError(null)

    try {
      const source = await createSource.mutateAsync(payload)
      navigate(`/storage-sources/${source.id}`)
    } catch (mutationError) {
      setSubmitError(getErrorMessage(mutationError, 'Unable to create storage source'))
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="heading-lg flex items-center gap-3">
            <HardDrive className="h-6 w-6 text-amber-400" />
            Storage Sources
          </h1>
          <p className="mt-1 text-slate-400">
            Register mounts, validate access, and prepare handshake inputs for ingestion.
          </p>
        </div>

        <button className="btn-secondary flex items-center gap-2" onClick={() => refetch()}>
          <RefreshCw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr,1.4fr]">
        <div className="card card-hover">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10">
              <Database className="h-5 w-5 text-amber-400" />
            </div>
            <div>
              <h2 className="heading-md">Create Storage Source</h2>
              <p className="text-sm text-slate-400">Use your active demo project or override the defaults if needed.</p>
            </div>
          </div>

          {defaultProject && (
            <div className="mb-4 rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100">
              Demo defaults loaded: <span className="font-medium">{defaultProject.name}</span> · org
              <span className="font-mono"> {defaultProject.organization_id}</span> · project
              <span className="font-mono"> {defaultProject.id}</span>
            </div>
          )}

          {projectsError && (
            <div className="mb-4 rounded-xl border border-amber-500/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
              {projectsError}
            </div>
          )}

          {submitError && (
            <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {submitError}
            </div>
          )}

          {projectsLoading ? (
            <div className="text-sm text-slate-400">Loading project defaults...</div>
          ) : (
            <StorageSourceForm
              key={defaultProject?.id ?? 'manual-storage-source-form'}
              mode="create"
              initialValues={defaultFormValues}
              submitLabel="Create Source"
              isSubmitting={createSource.isPending}
              onSubmit={handleCreateSource}
            />
          )}
        </div>

        <div className="card card-hover">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="heading-md">Available Sources</h2>
              <p className="text-sm text-slate-400">Visible sources in your current organization scope.</p>
            </div>
            <span className="rounded-full bg-white/5 px-3 py-1 text-xs font-medium text-slate-300">
              {sources?.length ?? 0} sources
            </span>
          </div>

          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {getErrorMessage(error, 'Unable to load storage sources')}
            </div>
          )}

          {isLoading && <div className="text-sm text-slate-400">Loading storage sources...</div>}

          {!isLoading && !error && (!sources || sources.length === 0) && (
            <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.02] px-6 py-10 text-center">
              <FolderOpen className="mx-auto mb-3 h-10 w-10 text-slate-500" />
              <p className="text-sm text-slate-400">No storage sources registered yet.</p>
            </div>
          )}

          <div className="space-y-4">
            {sources?.map((source) => (
              <article key={source.id} className="rounded-2xl border border-white/10 bg-dark-300/40 p-5">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="space-y-3">
                    <div className="flex flex-wrap items-center gap-3">
                      <h3 className="text-lg font-semibold text-white">{source.name}</h3>
                      <StorageStatusBadge status={source.status} />
                    </div>
                    <div className="grid gap-2 text-sm text-slate-300 md:grid-cols-2">
                      <p><span className="text-slate-500">Type:</span> {source.source_type}</p>
                      <p><span className="text-slate-500">Mount:</span> {source.mount_path}</p>
                      <p><span className="text-slate-500">Organization:</span> {source.organization_id}</p>
                      <p><span className="text-slate-500">Project:</span> {source.project_id}</p>
                    </div>
                  </div>

                  <Link to={`/storage-sources/${source.id}`} className="btn-secondary text-center">
                    Open Detail
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

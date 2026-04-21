import { useQuery } from '@tanstack/react-query'
import { opsApi } from '@/api'
import { useSystemOverview, useInstances, useCapabilities } from '@/hooks'
import { Settings, Server, Activity, RefreshCw, AlertTriangle, Cpu, Gauge, Layers, Sparkles, FolderKanban, Briefcase, Building2 } from 'lucide-react'
import clsx from 'clsx'

export default function AdminPage() {
  const { data: overview, isLoading: overviewLoading, refetch: refetchOverview } = useSystemOverview()
  const { data: instances } = useInstances()
  const { data: capabilities, refetch: refetchCapabilities } = useCapabilities()
  const { data: schedulerStatus } = useQuery({
    queryKey: ['adminSchedulerStatus'],
    queryFn: opsApi.getSchedulerStatus,
    refetchInterval: 30000,
  })
  const { data: projects } = useQuery({
    queryKey: ['adminProjects'],
    queryFn: opsApi.getAdminProjects,
    refetchInterval: 30000,
  })
  const { data: jobs } = useQuery({
    queryKey: ['adminJobs'],
    queryFn: opsApi.getAdminJobs,
    refetchInterval: 30000,
  })
  const { data: organizations } = useQuery({
    queryKey: ['adminOrganizations'],
    queryFn: opsApi.getAdminOrganizations,
    refetchInterval: 30000,
  })

  if (overviewLoading) {
    return (
      <div className="space-y-8">
        <div className="text-center">
          <div className="h-10 w-64 bg-slate-700 rounded mx-auto animate-pulse" />
        </div>
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-32 bg-slate-700 rounded" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="heading-lg flex items-center gap-3">
            <Settings className="w-6 h-6 text-amber-400" />
            Admin Panel
          </h1>
          <p className="text-slate-400 mt-1">System configuration and monitoring</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => refetchOverview()} className="btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button onClick={() => refetchCapabilities()} className="btn-secondary flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            Detect
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-4">
        <div className="stat-card group">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center group-hover:bg-blue-500/20 transition-colors">
              <Server className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Active Backends</p>
              <p className="text-3xl font-bold text-white">
                {instances?.available_backends || 0}
                <span className="text-lg text-slate-500">/{instances?.total_backends || 0}</span>
              </p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center group-hover:bg-amber-500/20 transition-colors">
              <Gauge className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Scheduler</p>
              <p className="text-lg font-semibold text-white">
                {overview?.scheduler?.running ? (
                  <span className="text-green-400 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                    Running
                  </span>
                ) : (
                  <span className="text-red-400 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-400" />
                    Stopped
                  </span>
                )}
              </p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center group-hover:bg-purple-500/20 transition-colors">
              <Layers className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Queued Jobs</p>
              <p className="text-3xl font-bold text-white">
                {Object.values(overview?.queue || {}).reduce((acc: number, q: any) => acc + (q.queue_size || 0), 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Backend Status & Capabilities */}
      <div className="grid grid-cols-2 gap-6">
        <div className="card card-hover">
          <div className="flex items-center gap-2 mb-6">
            <Cpu className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-semibold text-white">Backend Status</h2>
          </div>

          <div className="space-y-3">
            {instances?.backends && Object.entries(instances.backends).map(([key, backend]) => (
              <div key={key} className="p-4 rounded-xl bg-dark-300/50 border border-white/5 hover:border-amber-500/20 transition-all">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={clsx(
                      'w-3 h-3 rounded-full',
                      backend.healthy ? 'bg-green-400 shadow-lg shadow-green-400/50' : 'bg-red-500'
                    )} />
                    <span className="font-semibold text-white capitalize">{key}</span>
                  </div>
                  <span className="text-sm text-slate-500 font-mono">
                    {backend.base_url}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="p-2 rounded-lg bg-white/5">
                    <span className="text-slate-500 block mb-1">Jobs</span>
                    <span className="text-white font-medium">{backend.current_jobs}/{backend.max_concurrent_jobs}</span>
                  </div>
                  <div className="p-2 rounded-lg bg-white/5">
                    <span className="text-slate-500 block mb-1">Slots</span>
                    <span className="text-white font-medium">{backend.available_slots}</span>
                  </div>
                  <div className="p-2 rounded-lg bg-white/5">
                    <span className="text-slate-500 block mb-1">Status</span>
                    <span className={backend.enabled ? 'text-green-400' : 'text-slate-500'}>
                      {backend.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {(!instances?.backends || Object.keys(instances.backends).length === 0) && (
              <div className="text-center py-8 text-slate-500">
                No backends configured
              </div>
            )}
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center gap-2 mb-6">
            <Activity className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-semibold text-white">Detected Capabilities</h2>
          </div>

          <div className="space-y-3">
            {capabilities?.backends && Object.entries(capabilities.backends).map(([key, caps]) => (
              <div key={key} className="p-4 rounded-xl bg-dark-300/50 border border-white/5 hover:border-amber-500/20 transition-all">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-semibold text-white capitalize">{key}</span>
                  <span className="text-sm text-slate-500">
                    {caps.response_time_ms?.toFixed(0) || '?'}ms
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {caps.detected_capabilities?.map((cap) => (
                    <span key={cap} className="px-3 py-1 bg-amber-500/10 text-amber-400 rounded-lg text-xs font-medium border border-amber-500/20">
                      {cap}
                    </span>
                  ))}
                </div>
                {caps.warnings && caps.warnings.length > 0 && (
                  <div className="mt-3 flex items-center gap-2 text-amber-400 text-sm">
                    <AlertTriangle className="w-4 h-4" />
                    {caps.warnings[0]}
                  </div>
                )}
              </div>
            ))}
            {(!capabilities?.backends || Object.keys(capabilities.backends).length === 0) && (
              <div className="text-center py-8 text-slate-500">
                No capabilities detected
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Configuration Cards */}
      <div className="card">
        <h2 className="heading-md mb-6">Advanced Configuration</h2>
        <div className="grid grid-cols-4 gap-4">
          <button className="p-5 rounded-xl bg-dark-300/50 border border-white/5 hover:border-amber-500/20 hover:bg-dark-300 transition-all text-left group">
            <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center mb-3 group-hover:bg-amber-500/10 transition-colors">
              <Settings className="w-5 h-5 text-slate-400 group-hover:text-amber-400 transition-colors" />
            </div>
            <p className="font-medium text-white">General</p>
            <p className="text-sm text-slate-500">App settings</p>
          </button>
          <button className="p-5 rounded-xl bg-dark-300/50 border border-white/5 hover:border-amber-500/20 hover:bg-dark-300 transition-all text-left group">
            <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center mb-3 group-hover:bg-amber-500/10 transition-colors">
              <Server className="w-5 h-5 text-slate-400 group-hover:text-amber-400 transition-colors" />
            </div>
            <p className="font-medium text-white">Backends</p>
            <p className="text-sm text-slate-500">Instances</p>
          </button>
          <button className="p-5 rounded-xl bg-dark-300/50 border border-white/5 hover:border-amber-500/20 hover:bg-dark-300 transition-all text-left group">
            <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center mb-3 group-hover:bg-amber-500/10 transition-colors">
              <Layers className="w-5 h-5 text-slate-400 group-hover:text-amber-400 transition-colors" />
            </div>
            <p className="font-medium text-white">Workflows</p>
            <p className="text-sm text-slate-500">Templates</p>
          </button>
          <button className="p-5 rounded-xl bg-dark-300/50 border border-white/5 hover:border-amber-500/20 hover:bg-dark-300 transition-all text-left group">
            <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center mb-3 group-hover:bg-amber-500/10 transition-colors">
              <Gauge className="w-5 h-5 text-slate-400 group-hover:text-amber-400 transition-colors" />
            </div>
            <p className="font-medium text-white">Scheduler</p>
            <p className="text-sm text-slate-500">Queue config</p>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="card card-hover">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <FolderKanban className="w-5 h-5 text-amber-400" />
              <h2 className="text-lg font-semibold text-white">Projects</h2>
            </div>
            <span className="text-sm text-slate-500">{projects?.length || 0}</span>
          </div>
          <div className="space-y-3">
            {projects?.map((project) => (
              <div key={project.id} className="p-4 rounded-xl bg-dark-300/50 border border-white/5">
                <p className="font-medium text-white truncate">{project.name}</p>
                <p className="text-xs text-slate-500 font-mono truncate">org {project.organization_id}</p>
              </div>
            ))}
            {(!projects || projects.length === 0) && (
              <div className="text-center py-8 text-slate-500">No projects available</div>
            )}
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-amber-400" />
              <h2 className="text-lg font-semibold text-white">Jobs</h2>
            </div>
            <span className="text-sm text-slate-500">{jobs?.length || 0}</span>
          </div>
          <div className="space-y-3">
            {jobs?.map((job) => (
              <div key={job.id} className="p-4 rounded-xl bg-dark-300/50 border border-white/5">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-white truncate">{job.job_type}</p>
                  <span className="text-xs uppercase tracking-wide text-amber-400">{job.status}</span>
                </div>
                <p className="text-xs text-slate-500 font-mono truncate">project {job.project_id}</p>
              </div>
            ))}
            {(!jobs || jobs.length === 0) && (
              <div className="text-center py-8 text-slate-500">No jobs available</div>
            )}
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-amber-400" />
              <h2 className="text-lg font-semibold text-white">Organizations</h2>
            </div>
            <span className="text-sm text-slate-500">{organizations?.length || 0}</span>
          </div>
          <div className="space-y-3">
            {organizations?.map((organization) => (
              <div key={organization.id} className="p-4 rounded-xl bg-dark-300/50 border border-white/5">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-white truncate">{organization.name}</p>
                  <span className="text-xs text-slate-500">{organization.project_count} projects</span>
                </div>
                <p className="text-xs text-slate-500">{organization.job_count} jobs</p>
              </div>
            ))}
            {(!organizations || organizations.length === 0) && (
              <div className="text-center py-8 text-slate-500">No organizations available</div>
            )}
          </div>
        </div>
      </div>

      <div className="card card-hover">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-white">Scheduler Endpoint</h2>
            <p className="text-sm text-slate-500">Data sourced from /api/admin/scheduler/status</p>
          </div>
          <span className={clsx(
            'px-3 py-1 rounded-full text-xs font-semibold',
            schedulerStatus?.running ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
          )}>
            {schedulerStatus?.running ? 'Running' : 'Stopped'}
          </span>
        </div>
      </div>
    </div>
  )
}

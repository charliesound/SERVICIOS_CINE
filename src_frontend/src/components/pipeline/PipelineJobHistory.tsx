import { Clock3, RefreshCw, Waypoints } from 'lucide-react'
import type { PipelineJob } from '@/services/pipelineApi'

interface PipelineJobHistoryProps {
  jobs: PipelineJob[]
  isLoading: boolean
  onRefresh: () => void
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

export default function PipelineJobHistory({ jobs, isLoading, onRefresh }: PipelineJobHistoryProps) {
  return (
    <section className="card card-hover">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="heading-md">Historial de jobs simulated</h2>
          <p className="mt-1 text-sm text-slate-400">Scoped por usuario y organizacion; si defines proyecto, la vista tambien puede filtrarse por project ID.</p>
        </div>
        <button type="button" onClick={onRefresh} disabled={isLoading} className="btn-secondary flex items-center gap-2 self-start">
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Actualizar
        </button>
      </div>

      <div className="mt-6 space-y-4">
        {jobs.length === 0 ? (
          <div className="rounded-[1.5rem] border border-dashed border-white/10 bg-white/[0.03] px-5 py-8 text-sm text-slate-400">
            Todavia no hay jobs simulated. Ejecuta una simulacion para poblar el historial.
          </div>
        ) : jobs.map((job) => (
          <article key={job.job_id} className="rounded-[1.5rem] border border-white/8 bg-dark-300/55 p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs font-medium text-amber-100">
                    {job.status}
                  </span>
                  <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
                    {job.pipeline.preset_name}
                  </span>
                  <span className="rounded-full border border-cyan-400/10 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-100">
                    {job.task_type}
                  </span>
                </div>
                <h3 className="mt-3 text-lg font-semibold text-white">{job.pipeline.title}</h3>
                <p className="mt-1 font-mono text-xs text-slate-500">Job ID: {job.job_id}</p>
                <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-400">
                  <span className="inline-flex items-center gap-1"><Clock3 className="h-3.5 w-3.5" /> {formatDate(job.created_at)}</span>
                  <span>Pipeline: {job.pipeline_id}</span>
                  {job.project_id ? <span>Project: {job.project_id}</span> : <span>Scope: organization-wide</span>}
                </div>
              </div>

              <div className="min-w-[220px] rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm text-slate-300">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Validacion</p>
                <p className="mt-2 text-white">{job.validation.valid ? 'Lista para simulated execution' : 'Revisar advertencias o bloqueos'}</p>
                <p className="mt-1 text-xs text-slate-500">{job.validation.errors.length} errores · {job.validation.warnings.length} warnings</p>
              </div>
            </div>

            <div className="mt-5 rounded-2xl border border-white/6 bg-white/[0.02] p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-white">
                <Waypoints className="h-4 w-4 text-amber-300" />
                Timeline
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                {job.history.map((event) => (
                  <div key={event.id} className="rounded-xl border border-white/8 bg-dark-300/50 p-3">
                    <p className="text-xs uppercase tracking-[0.18em] text-cyan-300">{event.event_type}</p>
                    <p className="mt-2 text-sm font-medium text-white">{event.status}</p>
                    <p className="mt-1 text-sm text-slate-400">{event.message}</p>
                    <p className="mt-2 text-xs text-slate-500">{formatDate(event.created_at)}</p>
                  </div>
                ))}
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

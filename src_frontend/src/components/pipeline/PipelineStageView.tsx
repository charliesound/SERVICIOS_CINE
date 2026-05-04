import { ArrowRight, Boxes, Cable, Clapperboard } from 'lucide-react'
import type { PipelineDefinition } from '@/services/pipelineApi'

interface PipelineStageViewProps {
  pipeline: PipelineDefinition | null
}

export default function PipelineStageView({ pipeline }: PipelineStageViewProps) {
  if (!pipeline) {
    return (
      <section className="card card-hover">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-slate-300">
            <Boxes className="h-5 w-5" />
          </div>
          <div>
            <h2 className="heading-md">Vista de fases</h2>
            <p className="text-sm text-slate-400">Genera un pipeline para visualizar su secuencia de etapas.</p>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="card card-hover">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] text-amber-300">Pipeline generado</p>
          <h2 className="mt-2 heading-md">{pipeline.title}</h2>
          <p className="mt-1 text-sm text-slate-400">{pipeline.summary || 'Pipeline simulated listo para revisar y validar.'}</p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs text-slate-300">
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">{pipeline.task_type}</span>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">{pipeline.backend || 'simulated'}</span>
          <span className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-amber-200">{pipeline.preset_name}</span>
        </div>
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-2">
        {pipeline.stages.map((stage, index) => (
          <article key={stage.id} className="rounded-[1.5rem] border border-white/8 bg-dark-300/50 p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.22em] text-cyan-300">Stage {index + 1}</p>
                <h3 className="mt-2 text-lg font-semibold text-white">{stage.name}</h3>
                <p className="mt-1 text-sm text-slate-400">Tipo: {stage.type}</p>
              </div>
              <div className="rounded-2xl border border-amber-500/15 bg-amber-500/10 p-3 text-amber-200">
                <Clapperboard className="h-5 w-5" />
              </div>
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl border border-white/6 bg-white/[0.03] p-4">
                <div className="flex items-center gap-2 text-sm font-medium text-white">
                  <Cable className="h-4 w-4 text-cyan-300" />
                  Inputs
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {stage.inputs.length > 0 ? stage.inputs.map((item) => (
                    <span key={item} className="rounded-full border border-cyan-400/10 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-100">
                      {item}
                    </span>
                  )) : <span className="text-xs text-slate-500">Sin inputs declarados</span>}
                </div>
              </div>

              <div className="rounded-2xl border border-white/6 bg-white/[0.03] p-4">
                <div className="flex items-center gap-2 text-sm font-medium text-white">
                  <ArrowRight className="h-4 w-4 text-amber-300" />
                  Outputs
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {stage.outputs.length > 0 ? stage.outputs.map((item) => (
                    <span key={item} className="rounded-full border border-amber-400/10 bg-amber-400/10 px-3 py-1 text-xs text-amber-100">
                      {item}
                    </span>
                  )) : <span className="text-xs text-slate-500">Sin outputs declarados</span>}
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

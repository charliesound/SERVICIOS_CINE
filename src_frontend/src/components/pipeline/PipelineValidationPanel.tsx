import { AlertTriangle, CheckCircle2, ShieldAlert, Sparkles } from 'lucide-react'
import type { PipelineValidationResponse } from '@/services/pipelineApi'

interface PipelineValidationPanelProps {
  validation: PipelineValidationResponse | null
  suggestions: string[]
}

function ValidationList({
  title,
  items,
  tone,
}: {
  title: string
  items: Array<{ code: string; message: string; field?: string | null }>
  tone: 'error' | 'warning'
}) {
  const styles = tone === 'error'
    ? 'border-red-500/20 bg-red-500/10 text-red-100'
    : 'border-amber-500/20 bg-amber-500/10 text-amber-100'

  return (
    <div className={`rounded-2xl border p-4 ${styles}`}>
      <p className="text-sm font-semibold">{title}</p>
      <div className="mt-3 space-y-3 text-sm">
        {items.map((item) => (
          <div key={`${item.code}-${item.field || 'global'}`}>
            <p>{item.message}</p>
            {item.field ? <p className="mt-1 text-xs opacity-75">Campo: {item.field}</p> : null}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function PipelineValidationPanel({ validation, suggestions }: PipelineValidationPanelProps) {
  if (!validation) {
    return (
      <section className="card card-hover">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-slate-300">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div>
            <h2 className="heading-md">Validacion</h2>
            <p className="text-sm text-slate-400">Todavia no hay resultados de validacion para mostrar.</p>
          </div>
        </div>
      </section>
    )
  }

  const hasErrors = validation.errors.length > 0
  const hasWarnings = validation.warnings.length > 0

  return (
    <section className="card card-hover">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="heading-md">Panel de validacion</h2>
          <p className="mt-1 text-sm text-slate-400">Errores, warnings y sugerencias para revisar antes de ejecutar la simulacion.</p>
        </div>
        <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium ${validation.valid ? 'border border-green-500/20 bg-green-500/10 text-green-300' : 'border border-red-500/20 bg-red-500/10 text-red-200'}`}>
          {validation.valid ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
          {validation.valid ? 'Pipeline valido' : validation.blocked ? 'Bloqueado por validacion' : 'Requiere ajustes'}
        </div>
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-4">
          {hasErrors ? <ValidationList title="Errores" items={validation.errors} tone="error" /> : null}
          {hasWarnings ? <ValidationList title="Warnings" items={validation.warnings} tone="warning" /> : null}
          {!hasErrors && !hasWarnings ? (
            <div className="rounded-2xl border border-green-500/20 bg-green-500/10 p-4 text-sm text-green-100">
              La validacion estructural y el Legal Gate no detectan bloqueos ni advertencias activas.
            </div>
          ) : null}
        </div>

        <div className="rounded-[1.6rem] border border-white/8 bg-white/[0.03] p-5">
          <div className="flex items-center gap-2 text-white">
            <Sparkles className="h-4 w-4 text-cyan-300" />
            <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-200">Sugerencias</h3>
          </div>
          <div className="mt-4 space-y-3 text-sm leading-6 text-slate-300">
            {suggestions.length > 0 ? suggestions.map((suggestion) => (
              <p key={suggestion}>- {suggestion}</p>
            )) : <p>- Ejecuta una nueva validacion cuando cambies el prompt o el Legal Gate.</p>}
          </div>
        </div>
      </div>
    </section>
  )
}

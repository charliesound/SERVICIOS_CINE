import { ShieldCheck, Volume2 } from 'lucide-react'
import type { PipelineLegalContext, PipelineMode } from '@/services/pipelineApi'

interface LegalGatePanelProps {
  mode: PipelineMode
  legal: PipelineLegalContext
  onChange: (next: PipelineLegalContext) => void
}

export default function LegalGatePanel({ mode, legal, onChange }: LegalGatePanelProps) {
  const isDubbing = mode === 'dubbing'

  return (
    <section className="card card-hover">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/15 bg-cyan-400/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-cyan-200">
            <ShieldCheck className="h-3.5 w-3.5" />
            Legal Gate
          </div>
          <h2 className="mt-4 heading-md">Control legal previo a la simulacion</h2>
          <p className="mt-1 text-sm text-slate-400">
            El backend bloquea voice cloning en dubbing si no existe consentimiento explicito y advierte cuando faltan declaraciones de derechos.
          </p>
        </div>
        <div className="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 text-sm text-slate-300">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Modo actual</p>
          <p className="mt-2 text-base font-semibold capitalize text-white">{mode}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-[1.5rem] border border-white/8 bg-dark-300/50 p-5">
          <div className="flex items-center gap-2 text-white">
            <Volume2 className="h-4 w-4 text-amber-300" />
            <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-amber-100">Consentimiento y voz</h3>
          </div>

          <div className="mt-4 space-y-4">
            <label className={`flex items-start gap-3 rounded-xl border px-4 py-3 ${isDubbing ? 'border-white/10 bg-white/[0.03]' : 'border-white/6 bg-white/[0.02] opacity-60'}`}>
              <input
                type="checkbox"
                checked={legal.voice_cloning}
                disabled={!isDubbing}
                onChange={(event) => onChange({ ...legal, voice_cloning: event.target.checked })}
                className="mt-1"
              />
              <span>
                <span className="block text-sm font-medium text-white">Voice cloning</span>
                <span className="mt-1 block text-sm text-slate-400">Activalo solo si el pipeline usa clonacion de voz en dubbing.</span>
              </span>
            </label>

            <label className={`flex items-start gap-3 rounded-xl border px-4 py-3 ${isDubbing ? 'border-white/10 bg-white/[0.03]' : 'border-white/6 bg-white/[0.02] opacity-60'}`}>
              <input
                type="checkbox"
                checked={legal.consent}
                disabled={!isDubbing}
                onChange={(event) => onChange({ ...legal, consent: event.target.checked })}
                className="mt-1"
              />
              <span>
                <span className="block text-sm font-medium text-white">Consentimiento explicito</span>
                <span className="mt-1 block text-sm text-slate-400">Obligatorio cuando `voice_cloning=true` para que la validacion no quede bloqueada.</span>
              </span>
            </label>
          </div>
        </div>

        <div className="rounded-[1.5rem] border border-white/8 bg-dark-300/50 p-5">
          <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-100">Derechos y contexto</h3>

          <label className="mt-4 flex items-start gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3">
            <input
              type="checkbox"
              checked={legal.rights_declared}
              onChange={(event) => onChange({ ...legal, rights_declared: event.target.checked })}
              className="mt-1"
            />
            <span>
              <span className="block text-sm font-medium text-white">Declaracion de derechos</span>
              <span className="mt-1 block text-sm text-slate-400">Marca esta opcion si tienes ownership o licencias sobre el material fuente.</span>
            </span>
          </label>

          <div className="mt-4">
            <label className="label" htmlFor="legal-rights-notes">Notas de derechos</label>
            <textarea
              id="legal-rights-notes"
              value={legal.rights_notes || ''}
              onChange={(event) => onChange({ ...legal, rights_notes: event.target.value })}
              placeholder="Ejemplo: Guion original propio; referencias visuales con permiso interno para demo."
              className="input min-h-[132px] resize-y"
            />
          </div>
        </div>
      </div>
    </section>
  )
}

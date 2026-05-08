import { Brain, Cpu, Orbit, GitBranch } from 'lucide-react'
import LandingMediaBackground from '@/components/landing/LandingMediaBackground'
import { getLandingVisual } from '@/utils/landingVisuals'

const pipelineVisual = getLandingVisual('pipeline_orchestration')

const steps = [
  {
    icon: Brain,
    label: 'IA',
    title: 'Razona y estructura',
    text: 'Analiza el guion, identifica personajes, localizaciones y desglose técnico. Recomienda planos y encuadres.',
    color: 'emerald',
  },
  {
    icon: Cpu,
    label: 'ComfyUI',
    title: 'Genera la imagen',
    text: 'Workflows de Flux/SDXL para storyboard, concept art y previz. Control de estilo, iluminación y atmósfera.',
    color: 'violet',
  },
  {
    icon: Orbit,
    label: 'CID',
    title: 'Orquesta el flujo',
    text: 'Pipeline completo: guion → análisis → prompt visual → generación → revisión → entrega. Trazabilidad total.',
    color: 'amber',
  },
  {
    icon: GitBranch,
    label: 'Pipeline',
    title: 'Control de versiones',
    text: 'Cada decisión creativa queda registrada. Compara versiones, restaura estados anteriores y exporta el flujo completo.',
    color: 'cyan',
  },
]

const colorMap: Record<string, string> = {
  emerald: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
  violet: 'border-violet-500/30 bg-violet-500/10 text-violet-400',
  amber: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
  cyan: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-400',
}

const connectorMap: Record<string, string> = {
  emerald: 'bg-emerald-500/30',
  violet: 'bg-violet-500/30',
  amber: 'bg-amber-500/30',
  cyan: 'bg-cyan-500/30',
}

export default function LandingPipelineBuilder() {
  return (
    <section className="relative border-t border-white/5 py-28 md:py-36">
      <LandingMediaBackground
        className="landing-section-bg-img"
        imageSrc={pipelineVisual.imagePath}
        alt=""
        mediaClassName="h-full w-full object-cover opacity-[0.13]"
        overlayClassName="absolute inset-0 bg-gradient-to-t from-[#080808] via-transparent to-[#080808]"
        imageLoading="lazy"
      />
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-400">
            Pipeline Builder
          </p>
          <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
            De la idea a la entrega, <br />
            <span className="text-gradient-amber">sin fricción.</span>
          </h2>
          <p className="mt-4 text-lg leading-8 text-slate-400">
            La IA estructura, razona y recomienda. ComfyUI genera la imagen. CID orquesta el flujo 
            completo con trazabilidad y control creativo.
          </p>
        </div>

        <div className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, i) => (
            <div key={step.title} className="landing-pipeline-step group">
              <div className="landing-pipeline-step-header">
                <div className={`inline-flex h-12 w-12 items-center justify-center rounded-2xl border ${colorMap[step.color]}`}>
                  <step.icon className="h-6 w-6" />
                </div>
                <span className={`landing-pipeline-step-number ${connectorMap[step.color]}`}>
                  {String(i + 1).padStart(2, '0')}
                </span>
              </div>
              <span className="mt-4 inline-block rounded-full border border-white/10 bg-white/5 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.2em] text-slate-400">
                {step.label}
              </span>
              <h3 className="mt-3 text-lg font-semibold text-white">{step.title}</h3>
              <p className="mt-2 text-sm leading-7 text-slate-400">{step.text}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 flex items-center justify-center gap-3">
          <div className="h-px w-8 bg-amber-500/30" />
          <span className="font-mono text-[10px] uppercase tracking-[0.24em] text-slate-500">
            Guion &rarr; Análisis &rarr; Prompt visual &rarr; ComfyUI &rarr; Storyboard &rarr; Revisión &rarr; Entrega
          </span>
          <div className="h-px w-8 bg-amber-500/30" />
        </div>

        <div className="mt-12 rounded-[2rem] border border-white/10 bg-white/[0.03] p-6 backdrop-blur-sm">
          <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-amber-300">
                Qué debe verse en la imagen del pipeline
              </p>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
                {pipelineVisual.visualConcept}
              </p>
              <div className="mt-4 flex flex-wrap gap-3">
                {pipelineVisual.continuityRules.map((rule) => (
                  <span
                    key={rule}
                    className="rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-xs text-slate-400"
                  >
                    {rule}
                  </span>
                ))}
              </div>
            </div>

            <div className="rounded-[1.5rem] border border-white/10 bg-black/20 p-5">
              <div className="flex items-center justify-between gap-3 text-[10px] uppercase tracking-[0.24em] text-slate-400">
                <span>Ollama / CID / ComfyUI</span>
                <span className="text-amber-300">validacion narrativa</span>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
                {[
                  'Guion y briefing',
                  'Interpretacion y desglose',
                  'Prompt visual consistente',
                  'Generacion controlada',
                  'Revision y continuidad',
                  'Entrega trazable',
                ].map((item, index) => (
                  <div key={item} className="rounded-2xl border border-white/8 bg-white/[0.02] px-4 py-3 text-sm text-slate-300">
                    <span className="mr-2 text-amber-300">0{index + 1}</span>
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

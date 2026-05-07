import { Brain, Cpu, Orbit, GitBranch } from 'lucide-react'

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
      <div className="landing-section-bg-img">
        <img
          src="/landing-media/pipeline-frame.webp"
          alt=""
          className="h-full w-full object-cover opacity-[0.04]"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#080808] via-transparent to-[#080808]" />
      </div>
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
      </div>
    </section>
  )
}

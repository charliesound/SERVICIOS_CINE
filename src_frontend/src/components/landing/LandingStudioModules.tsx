import { FileSearch, Image as ImageIcon, Clapperboard, Cpu } from 'lucide-react'
import { getLandingVisual } from '@/utils/landingVisuals'

const modules = [
  {
    icon: FileSearch,
    title: 'Análisis de guion',
    description:
      'Desglose automático de guion con identificación de personajes, localizaciones, planos y necesidades de producción.',
    visualId: 'script_analysis_breakdown',
  },
  {
    icon: ImageIcon,
    title: 'Moodboards visuales',
    description:
      'Construye referencias visuales por escena, personaje y atmósfera. Consolida la dirección artística antes del rodaje.',
    visualId: 'moodboard_bible',
  },
  {
    icon: Clapperboard,
    title: 'Storyboards cinematográficos',
    description:
      'Genera storyboards por plano con encuadre, ángulo e iluminación. Mantén continuidad visual entre escenas.',
    visualId: 'storyboard_sequence',
  },
  {
    icon: Cpu,
    title: 'Generacion visual controlada',
    description:
      'CID prepara el prompt, ComfyUI genera el frame y el sistema valida coherencia antes de pasar a storyboard o revision.',
    visualId: 'comfyui_generation_engine',
  },
]

const moduleCards = modules.map((module) => ({
  ...module,
  visual: getLandingVisual(module.visualId),
}))

export default function LandingStudioModules() {
  return (
    <section className="relative py-28 md:py-36">
      <div className="landing-section-glow-left" />
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-400">
            The AI Film Operating System
          </p>
          <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
            Tu flujo de trabajo audiovisual, potenciado por IA
          </h2>
          <p className="mt-4 text-lg leading-8 text-slate-400">
          Desde el guion hasta la entrega, CID conecta cada fase del pipeline con inteligencia artificial entrenada para cine.
          </p>
        </div>

        <div className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {moduleCards.map((mod) => (
            <div key={mod.title} className="landing-studio-module-card group">
              <div className="landing-studio-module-image">
                <img
                  src={mod.visual.imagePath}
                  alt={mod.visual.visualConcept}
                  className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#080808] via-[#080808]/40 to-transparent" />
              </div>
              <div className="relative z-10 -mt-8 space-y-3 px-5 pb-6 pt-2">
                <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-amber-500/20 bg-amber-500/10 text-amber-400 backdrop-blur-sm">
                  <mod.icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-semibold text-white">{mod.title}</h3>
                <p className="text-sm leading-7 text-slate-400">{mod.description}</p>
                <p className="text-xs leading-6 text-slate-500">{mod.visual.narrativePurpose}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

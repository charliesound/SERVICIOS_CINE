import { AlertTriangle, Cpu, Orbit, GitBranch, Zap } from 'lucide-react'
import LandingMediaBackground from '@/components/landing/LandingMediaBackground'
import { getLandingVisual } from '@/utils/landingVisuals'

const problemVisual = getLandingVisual('fragmented_departments')

const problems = [
  {
    icon: AlertTriangle,
    title: 'Flujos desconectados',
    text: 'Guion, storyboard, producción y post suelen operar en entornos separados. Cada fase pierde contexto de la anterior.',
  },
  {
    icon: Cpu,
    title: 'IA sin dirección',
    text: 'La IA generativa produce imágenes, pero sin integración en un pipeline real el resultado se queda en piezas sueltas sin continuidad.',
  },
  {
    icon: GitBranch,
    title: 'Falta de control técnico',
    text: 'Sin trazabilidad, versionado ni supervisión por departamento, las decisiones creativas se vuelven difíciles de gestionar.',
  },
]

export default function LandingProblemSolution() {
  return (
    <section className="relative border-t border-white/5 py-28 md:py-36">
      <div className="landing-section-glow-left" />
      <LandingMediaBackground
        className="landing-section-bg-img"
        imageSrc={problemVisual.imagePath}
        alt=""
        mediaClassName="h-full w-full object-cover opacity-[0.13]"
        overlayClassName="absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-[#080808]"
        imageLoading="lazy"
      />
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-400">
            El problema
          </p>
          <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
            La producción audiovisual sigue <span className="text-gradient-amber">fragmentada</span>
          </h2>
          <p className="mt-4 text-lg leading-8 text-slate-400">
            Las herramientas de IA aparecen cada semana, pero ninguna está diseñada para integrarse en un flujo de producción real.
          </p>
        </div>

        <div className="mt-14 grid gap-5 md:grid-cols-3">
          {problems.map((p) => (
            <div key={p.title} className="landing-creative-card">
              <div className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-red-500/20 bg-red-500/10 text-red-400">
                <p.icon className="h-5 w-5" />
              </div>
              <h3 className="mt-4 text-base font-semibold text-white">{p.title}</h3>
              <p className="mt-2 text-sm leading-7 text-slate-400">{p.text}</p>
            </div>
          ))}
        </div>

        <div className="relative mt-20 overflow-hidden rounded-[2rem] border border-amber-500/20 bg-gradient-to-br from-amber-500/10 via-transparent to-amber-500/5 p-8 md:p-12">
          <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-amber-500/10 blur-3xl" />
          <div className="relative z-10 flex flex-col items-center gap-6 text-center md:flex-row md:text-left">
            <div className="inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-amber-500/30 bg-amber-500/10 text-amber-400">
              <Orbit className="h-7 w-7" />
            </div>
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-400">
                La solución &mdash; CID
              </p>
              <h3 className="mt-2 font-display text-3xl font-semibold text-white md:text-4xl">
                Centro operativo inteligente para producción audiovisual
              </h3>
              <p className="mt-3 max-w-2xl text-base leading-7 text-slate-300">
                CID conecta guion, análisis, storyboard, concept art y delivery en un mismo flujo. 
                No es un generador de imágenes: es un sistema de producción asistido por IA, 
                con trazabilidad, control de versiones y supervisión por departamento.
              </p>
            </div>
            <div className="hidden shrink-0 md:block">
              <Zap className="h-10 w-10 text-amber-400/40" />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

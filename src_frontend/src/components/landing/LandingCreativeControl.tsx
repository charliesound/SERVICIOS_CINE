import { Palette, Users, RefreshCw, Eye, Layers, Download } from 'lucide-react'

const controls = [
  {
    icon: Palette,
    title: 'Dirección visual',
    text: 'Define paletas de color, iluminación y atmósfera por escena. Consolida la identidad visual del proyecto.',
  },
  {
    icon: Users,
    title: 'Colaboración',
    text: 'Comparte storyboards, moodboards y versiones con tu equipo. Comentarios contextuales por plano.',
  },
  {
    icon: RefreshCw,
    title: 'Versionado',
    text: 'Cada cambio queda registrado. Compara, restaura o bifurca versiones sin perder el historial.',
  },
  {
    icon: Eye,
    title: 'Casting visual',
    text: 'Referencias de personajes por actor, edad, vestuario y expresión. Consistencia en todo el proyecto.',
  },
  {
    icon: Layers,
    title: 'Continuidad',
    text: 'Los planos mantienen coherencia narrativa y visual entre escenas. Detección de saltos de raccord.',
  },
  {
    icon: Download,
    title: 'Exportación',
    text: 'Exporta tu storyboard en formatos profesionales: PDF, imagen, video o integración con herramientas de edición.',
  },
]

export default function LandingCreativeControl() {
  return (
    <section className="relative border-t border-white/5 py-28 md:py-36">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-400">
            Control creativo
          </p>
          <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
            Control total sobre tu <span className="text-gradient-amber">visión creativa</span>
          </h2>
          <p className="mt-4 text-lg leading-8 text-slate-400">
            Dirige cada aspecto de tu proyecto con herramientas diseñadas para equipos de cine y audiovisual.
          </p>
        </div>

        <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {controls.map((ctrl) => (
            <div key={ctrl.title} className="landing-creative-card group">
              <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-amber-400 transition-colors group-hover:border-amber-500/30 group-hover:bg-amber-500/10">
                <ctrl.icon className="h-5 w-5" />
              </div>
              <h3 className="mt-4 text-base font-semibold text-white">{ctrl.title}</h3>
              <p className="mt-2 text-sm leading-7 text-slate-400">{ctrl.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

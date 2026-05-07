import { Briefcase, Film, PanelsTopLeft, LayoutTemplate } from 'lucide-react'

const items = [
  {
    icon: Briefcase,
    title: 'Productoras y estudios',
    text: 'Para equipos que quieren ordenar desarrollo, operativa, materiales y control de proyecto.',
    accent: 'amber',
  },
  {
    icon: Film,
    title: 'Dirección y desarrollo creativo',
    text: 'Para quienes necesitan acelerar decisiones narrativas, visuales y de presentación.',
    accent: 'violet',
  },
  {
    icon: PanelsTopLeft,
    title: 'Producción y coordinación',
    text: 'Para quienes trabajan con fases, aprobaciones, dependencias y entregables reales.',
    accent: 'cyan',
  },
  {
    icon: LayoutTemplate,
    title: 'Post, delivery y partners',
    text: 'Para áreas que necesitan trazabilidad, QC y continuidad desde origen hasta entrega.',
    accent: 'emerald',
  },
]

const accentBorders: Record<string, string> = {
  amber: 'hover:border-amber-500/30',
  violet: 'hover:border-violet-500/30',
  cyan: 'hover:border-cyan-500/30',
  emerald: 'hover:border-emerald-500/30',
}

const accentIcons: Record<string, string> = {
  amber: 'text-amber-400 group-hover:text-amber-300',
  violet: 'text-violet-400 group-hover:text-violet-300',
  cyan: 'text-cyan-400 group-hover:text-cyan-300',
  emerald: 'text-emerald-400 group-hover:text-emerald-300',
}

export default function LandingAudienceB2B() {
  return (
    <section className="relative border-t border-white/5 py-28 md:py-36">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-400">
            Para productoras, directores y equipos técnicos
          </p>
          <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
            Construido para <span className="text-gradient-amber">flujos reales</span>
          </h2>
          <p className="mt-4 text-lg leading-8 text-slate-400">
            Una plataforma diseñada para equipos que producen, desarrollan y entregan cine y audiovisual.
          </p>
        </div>

        <div className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {items.map((item) => (
            <div
              key={item.title}
              className={`landing-creative-card group cursor-default ${accentBorders[item.accent]}`}
            >
              <div className={`transition-colors ${accentIcons[item.accent]}`}>
                <item.icon className="h-8 w-8" />
              </div>
              <h3 className="mt-4 text-base font-semibold text-white">{item.title}</h3>
              <p className="mt-2 text-sm leading-7 text-slate-400">{item.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

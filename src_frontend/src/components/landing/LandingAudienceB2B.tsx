import LandingMediaBackground from '@/components/landing/LandingMediaBackground'
import { getLandingVisual } from '@/utils/landingVisuals'

const b2bVisual = getLandingVisual('production_b2b_dashboard')

const items = [
  {
    title: 'Productoras y estudios',
    text: 'Para equipos que necesitan ordenar desarrollo, operativa, materiales y control de proyecto en un mismo entorno.',
    accent: 'amber',
  },
  {
    title: 'Dirección y desarrollo creativo',
    text: 'Para quienes necesitan acelerar decisiones narrativas y visuales sin perder control sobre el resultado final.',
    accent: 'violet',
  },
  {
    title: 'Producción y coordinación',
    text: 'Para equipos que trabajan con fases, aprobaciones, dependencias y entregables reales.',
    accent: 'cyan',
  },
  {
    title: 'Post, delivery y distribución',
    text: 'Para áreas que necesitan trazabilidad, QC y continuidad desde el origen hasta la entrega final.',
    accent: 'emerald',
  },
]

const accentBorders: Record<string, string> = {
  amber: 'border-l-amber-500/50',
  violet: 'border-l-violet-500/50',
  cyan: 'border-l-cyan-500/50',
  emerald: 'border-l-emerald-500/50',
}

const accentDots: Record<string, string> = {
  amber: 'bg-amber-500',
  violet: 'bg-violet-500',
  cyan: 'bg-cyan-500',
  emerald: 'bg-emerald-500',
}

export default function LandingAudienceB2B() {
  return (
    <section className="relative border-t border-white/5 py-28 md:py-36">
      <LandingMediaBackground
        className="landing-section-bg-img"
        imageSrc={b2bVisual.imagePath}
        alt=""
        mediaClassName="h-full w-full object-cover opacity-[0.13]"
        overlayClassName="absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-[#080808]"
        imageLoading="lazy"
      />
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-400">
            Para quién es
          </p>
          <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
            Construido para <span className="text-gradient-amber">flujos de producción reales</span>
          </h2>
          <p className="mt-4 text-lg leading-8 text-slate-400">
          Diseñado para productoras, directores y equipos técnicos que necesitan un sistema, no solo herramientas sueltas.
          </p>
        </div>

        <div className="mt-16 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {items.map((item) => (
            <div
              key={item.title}
              className={`landing-audience-card ${accentBorders[item.accent]}`}
            >
              <span className={`mb-3 inline-flex h-2 w-2 rounded-full ${accentDots[item.accent]}`} />
              <h3 className="text-base font-semibold text-white">{item.title}</h3>
              <p className="mt-2 text-sm leading-7 text-slate-400">{item.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

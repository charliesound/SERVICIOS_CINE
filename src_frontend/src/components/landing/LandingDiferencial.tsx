import { Sparkles, ShieldCheck, Scale, BadgeCheck, Layers, Eye } from 'lucide-react'
import LandingMediaBackground from '@/components/landing/LandingMediaBackground'
import { getLandingVisual } from '@/utils/landingVisuals'

const differentialVisual = getLandingVisual('professional_traceability')

const items = [
  {
    icon: Sparkles,
    title: 'IA con contexto de producción',
    text: 'No genera imágenes sueltas: entiende guion, personajes, localizaciones y continuidad narrativa antes de proponer un plano.',
  },
  {
    icon: ShieldCheck,
    title: 'Trazabilidad total',
    text: 'Cada decisión creativa, cada versión y cada aprobación quedan registradas. El equipo sabe qué se decidió, cuándo y por qué.',
  },
  {
    icon: Scale,
    title: 'Supervisión humana real',
    text: 'La IA acelera, pero las decisiones de calidad y entrega permanecen controladas por el director, el productor y el equipo técnico.',
  },
  {
    icon: BadgeCheck,
    title: 'Integración en flujos reales',
    text: 'No es una herramienta aislada. Se adapta al pipeline existente de la productora, con respeto por los roles y procesos de industria.',
  },
  {
    icon: Layers,
    title: 'De la idea al delivery',
    text: 'Guion, storyboard, concept art, producción, doblaje, sonido, VFX, montaje y entrega. Todo conectado en un mismo sistema operativo.',
  },
  {
    icon: Eye,
    title: 'Hecho para equipos de cine',
    text: 'Diseñado con criterio de producción real. No asume que el usuario es un prompt engineer: asume que es un director, productor o técnico.',
  },
]

export default function LandingDiferencial() {
  return (
    <section className="relative border-t border-white/5 py-28 md:py-36">
      <LandingMediaBackground
        className="landing-section-bg-img"
        imageSrc={differentialVisual.imagePath}
        alt=""
        mediaClassName="h-full w-full object-cover opacity-[0.13]"
        overlayClassName="absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-[#080808]"
        imageLoading="lazy"
      />
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-400">
            Diferencial profesional
          </p>
          <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
            Más que un generador de imágenes.<br />
            <span className="text-gradient-amber">Un sistema de producción.</span>
          </h2>
          <p className="mt-4 text-lg leading-8 text-slate-400">
            La mayoría de herramientas de IA generan contenido. CID organiza, conecta y controla todo el flujo de producción audiovisual.
          </p>
        </div>

        <div className="mt-16 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <div key={item.title} className="landing-diferencial-card group">
              <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-amber-500/20 bg-amber-500/10 text-amber-400 transition-colors group-hover:bg-amber-500/20">
                <item.icon className="h-5 w-5" />
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

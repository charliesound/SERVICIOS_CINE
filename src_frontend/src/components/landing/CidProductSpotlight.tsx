import { ArrowRight, ChevronRight } from 'lucide-react'
import LandingActionButton from '@/components/landing/LandingActionButton'
import type { LucideIcon } from 'lucide-react'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

interface CidProductSpotlightProps {
  content: {
    eyebrow: string
    badge: string
    title: string
    description: string
    priceLine: string
    supportLine: string
    departmentLine: string
    phases: readonly string[]
    highlights: readonly {
      icon: LucideIcon
      title: string
      text: string
    }[]
  }
}

export default function CidProductSpotlight({ content }: CidProductSpotlightProps) {
  return (
    <section id="cid" className="relative border-y border-white/10 bg-[#09111c]/80 py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
        <LandingReveal>
          <LandingSectionHeading
            eyebrow={content.eyebrow}
            title={content.title}
            description={content.description}
          />
        </LandingReveal>

        <div className="mt-14 grid gap-6 xl:grid-cols-[0.52fr_0.48fr] xl:items-start">
          <LandingReveal>
            <div className="landing-brand-cid-spotlight">
              <div className="flex items-center justify-between gap-4 border-b border-white/10 pb-5">
                <div>
                  <p className="editorial-kicker text-amber-300">{content.badge}</p>
                </div>
                <span className="rounded-full border border-cyan-300/15 bg-cyan-300/10 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-cyan-100">
                  sistema + departamentos
                </span>
              </div>

              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <div className="rounded-[1.3rem] border border-white/10 bg-white/[0.04] p-4">
                  <p className="text-[10px] uppercase tracking-[0.24em] text-amber-200">Creatividad + Canvas</p>
                  <p className="mt-3 text-sm leading-7 text-slate-200">Lienzo colaborativo conectado al pipeline de produccion real.</p>
                </div>
                <div className="rounded-[1.3rem] border border-white/10 bg-white/[0.04] p-4">
                  <p className="text-[10px] uppercase tracking-[0.24em] text-cyan-100">Produccion + IA</p>
                  <p className="mt-3 text-sm leading-7 text-slate-200">{content.supportLine}</p>
                </div>
              </div>

              <div className="mt-6">
                <p className="text-[11px] uppercase tracking-[0.24em] text-slate-400">Lienzo creativo + departamentos</p>
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {content.phases.map((phase, index) => (
                  <div key={phase} className="rounded-[1.2rem] border border-white/10 bg-white/[0.03] px-4 py-4">
                    <div className="flex items-center gap-3">
                      <div className="landing-brand-phase-marker">{index + 1}</div>
                      <p className="text-sm font-medium text-white">{phase}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 rounded-[1.3rem] border border-cyan-300/15 bg-cyan-300/10 px-4 py-4 text-sm leading-7 text-cyan-50">
                {content.departmentLine}
              </div>
            </div>
          </LandingReveal>

          <div className="grid gap-5">
            {content.highlights.map((item, index) => {
              const Icon = item.icon
              return (
                <LandingReveal key={item.title} delay={index * 95}>
                  <div className="landing-panel rounded-[1.7rem] p-6">
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                        <Icon className="h-5 w-5" />
                      </div>
                      <span className="text-[11px] uppercase tracking-[0.22em] text-slate-500">CID layer</span>
                    </div>
                    <h3 className="mt-5 text-2xl font-semibold text-white">{item.title}</h3>
                    <p className="mt-3 text-sm leading-7 text-slate-300">{item.text}</p>
                  </div>
                </LandingReveal>
              )
            })}

            <LandingReveal delay={260}>
              <div className="flex flex-col gap-3 sm:flex-row">
                <LandingActionButton destination="/solutions/cid" variant="primary">
                  Explorar CID
                  <ArrowRight className="h-4 w-4" />
                </LandingActionButton>
                <LandingActionButton destination="/pricing" variant="secondary">
                  Ver precios
                  <ChevronRight className="h-4 w-4" />
                </LandingActionButton>
              </div>
            </LandingReveal>
          </div>
        </div>
      </div>
    </section>
  )
}

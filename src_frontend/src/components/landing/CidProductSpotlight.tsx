import type { LucideIcon } from 'lucide-react'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

interface CidProductSpotlightProps {
  content: {
    eyebrow: string
    badge: string
    title: string
    description: string
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
                  <p className="mt-3 text-sm leading-7 text-slate-300">
                    El producto principal de AILinkCinema para estructurar el proyecto cinematografico como sistema y no como suma de herramientas aisladas.
                  </p>
                </div>
                <span className="rounded-full border border-cyan-300/15 bg-cyan-300/10 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-cyan-100">
                  flagship product
                </span>
              </div>

              <div className="mt-6 landing-brand-phase-track">
                {content.phases.map((phase, index) => (
                  <div key={phase} className="landing-brand-phase-row">
                    <div className="landing-brand-phase-marker">{index + 1}</div>
                    <div className="landing-brand-phase-surface">
                      <p className="text-sm font-medium text-white">{phase}</p>
                    </div>
                  </div>
                ))}
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
          </div>
        </div>
      </div>
    </section>
  )
}

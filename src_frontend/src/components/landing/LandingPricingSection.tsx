import { ArrowRight, ChevronRight } from 'lucide-react'
import LandingActionButton from '@/components/landing/LandingActionButton'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

interface LandingPricingSectionProps {
  content: {
    eyebrow: string
    title: string
    description: string
    cidSetup: string
    cidMonthly: string
    modulePricing: string
    custom: string
    bullets: readonly string[]
  }
}

export default function LandingPricingSection({ content }: LandingPricingSectionProps) {
  return (
    <section id="pricing" className="relative border-y border-white/10 bg-[#09111c]/76 py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
        <LandingReveal>
          <LandingSectionHeading
            eyebrow={content.eyebrow}
            title={content.title}
            description={content.description}
          />
        </LandingReveal>

        <div className="mt-14 grid gap-6 xl:grid-cols-[0.58fr_0.42fr]">
          <LandingReveal>
            <div className="landing-brand-pricing-panel rounded-[2rem] p-6 sm:p-7">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.05] p-5">
                  <p className="text-[11px] uppercase tracking-[0.22em] text-amber-200">CID setup</p>
                  <p className="mt-3 font-display text-4xl text-white">1.500 EUR+</p>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{content.cidSetup}</p>
                </div>

                <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.05] p-5">
                  <p className="text-[11px] uppercase tracking-[0.22em] text-cyan-200">CID mensual</p>
                  <p className="mt-3 font-display text-4xl text-white">299 EUR/mes+</p>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{content.cidMonthly}</p>
                </div>

                <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.04] p-5 md:col-span-2">
                  <p className="text-[11px] uppercase tracking-[0.22em] text-slate-400">Modulos y proyectos a medida</p>
                  <div className="mt-4 grid gap-4 lg:grid-cols-2">
                    <div>
                      <p className="text-lg font-semibold text-white">Desde 49 EUR/mes por app</p>
                      <p className="mt-2 text-sm leading-7 text-slate-300">{content.modulePricing}</p>
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-white">Desarrollo bajo presupuesto</p>
                      <p className="mt-2 text-sm leading-7 text-slate-300">{content.custom}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </LandingReveal>

          <LandingReveal delay={120}>
            <div className="landing-panel flex h-full flex-col justify-between rounded-[2rem] p-6 sm:p-7">
              <div>
                <p className="text-[11px] uppercase tracking-[0.22em] text-amber-200">Modelo comercial</p>
                <div className="mt-5 space-y-3">
                  {content.bullets.map((bullet) => (
                    <div key={bullet} className="rounded-[1.2rem] border border-white/10 bg-white/[0.03] px-4 py-4 text-sm leading-7 text-slate-200">
                      {bullet}
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row xl:flex-col">
                <LandingActionButton destination="/pricing" variant="primary">
                  Ver precios
                  <ArrowRight className="h-4 w-4" />
                </LandingActionButton>
                <LandingActionButton destination="/solutions/cid" variant="secondary">
                  Explorar CID
                  <ChevronRight className="h-4 w-4" />
                </LandingActionButton>
              </div>
            </div>
          </LandingReveal>
        </div>
      </div>
    </section>
  )
}

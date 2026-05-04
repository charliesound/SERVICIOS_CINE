import { ArrowRight, ChevronRight, Sparkles } from 'lucide-react'
import LandingActionButton from '@/components/landing/LandingActionButton'

type HeroTone = 'amber' | 'cyan' | 'violet' | 'emerald' | 'rose'

interface BrandHeroSectionProps {
  content: {
    eyebrow: string
    title: string
    subtitle: string
    differentialLine: string
    description: string
    chips: readonly string[]
    proof: readonly { label: string; text: string }[]
    visualProducts: readonly { name: string; label: string; tone: HeroTone }[]
    heroCore: {
      eyebrow: string
      title: string
      subtitle: string
      description: string
      phases: readonly string[]
    }
  }
  exploreCidTarget: string
  solutionsTarget: string
  requestDemoTarget: string
}

const toneClasses: Record<HeroTone, string> = {
  amber: 'landing-brand-product-tile-amber',
  cyan: 'landing-brand-product-tile-cyan',
  violet: 'landing-brand-product-tile-violet',
  emerald: 'landing-brand-product-tile-emerald',
  rose: 'landing-brand-product-tile-rose',
}

export default function BrandHeroSection({
  content,
  exploreCidTarget,
  solutionsTarget,
  requestDemoTarget,
}: BrandHeroSectionProps) {
  return (
    <section className="relative overflow-hidden pt-28 md:pt-36 lg:pt-40">
      <div className="landing-hero-radial" />
      <div className="mx-auto grid max-w-7xl gap-14 px-5 pb-24 md:px-6 lg:grid-cols-[1.02fr_0.98fr] lg:items-center lg:px-8 lg:pb-28">
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-300/20 bg-amber-300/10 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-amber-200">
            <Sparkles className="h-3.5 w-3.5" />
            {content.eyebrow}
          </div>

          <h1 className="mt-7 max-w-5xl font-display text-5xl font-semibold leading-[0.88] tracking-[-0.04em] text-white sm:text-6xl md:text-7xl xl:text-[6.1rem]">
            {content.title}
          </h1>

          <p className="mt-6 max-w-3xl text-lg font-medium leading-8 text-slate-100 md:text-2xl md:leading-10">
            {content.subtitle}
          </p>
          <div className="mt-5 inline-flex max-w-3xl rounded-[1.4rem] border border-cyan-300/15 bg-cyan-300/10 px-4 py-3 text-sm leading-7 text-cyan-50 backdrop-blur-xl md:text-base">
            {content.differentialLine}
          </div>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-400 md:text-lg md:leading-8">{content.description}</p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <LandingActionButton destination={exploreCidTarget} variant="primary">
                Ver CID: Creatividad + Produccion
                <ArrowRight className="h-4 w-4" />
              </LandingActionButton>
              <LandingActionButton destination={solutionsTarget} variant="secondary">
                Canvas + IA + Produccion
                <ChevronRight className="h-4 w-4" />
              </LandingActionButton>
              <LandingActionButton destination={requestDemoTarget} variant="ghost">
                Unir creatividad y produccion
              </LandingActionButton>
            </div>

          <div className="mt-8 flex flex-wrap gap-2.5">
            {content.chips.map((chip) => (
              <span key={chip} className="landing-pill">
                {chip}
              </span>
            ))}
          </div>

          <div className="mt-10 grid gap-3 sm:grid-cols-3">
            {content.proof.map((item) => (
              <div key={item.label} className="landing-brand-mini-panel">
                <p className="text-[11px] uppercase tracking-[0.22em] text-amber-200">{item.label}</p>
                <p className="mt-3 text-sm leading-6 text-slate-200">{item.text}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 landing-parallax-float">
          <div className="landing-brand-hero-panel">
            <div className="landing-brand-grid-lines" />
            <div className="relative z-10 grid gap-4 lg:grid-cols-[0.88fr_1.12fr]">
              <div className="space-y-4">
                {content.visualProducts.map((product) => (
                  <div key={product.name} className={`landing-brand-product-tile ${toneClasses[product.tone]}`}>
                    <p className="text-[10px] uppercase tracking-[0.24em] text-white/60">App especializada</p>
                    <h3 className="mt-2 text-base font-semibold text-white">{product.name}</h3>
                    <p className="mt-2 text-sm text-slate-200">{product.label}</p>
                  </div>
                ))}
              </div>

              <div className="landing-brand-cid-core">
                <p className="text-[10px] uppercase tracking-[0.28em] text-amber-200">{content.heroCore.eyebrow}</p>
                <h3 className="mt-4 font-display text-5xl text-white md:text-6xl">{content.heroCore.title}</h3>
                <p className="mt-2 text-lg font-medium text-slate-100">{content.heroCore.subtitle}</p>
                <p className="mt-4 text-sm leading-7 text-slate-300">{content.heroCore.description}</p>

                <div className="mt-6 flex flex-wrap gap-2.5">
                  {content.heroCore.phases.map((phase) => (
                    <span key={phase} className="landing-brand-phase-chip">
                      {phase}
                    </span>
                  ))}
                </div>

                <div className="mt-8 rounded-[1.4rem] border border-white/10 bg-white/[0.03] p-4">
                  <p className="text-[10px] uppercase tracking-[0.24em] text-slate-500">AILinkCinema stack</p>
                  <p className="mt-3 text-sm leading-7 text-slate-300">
                    Marca principal arriba. CID como sistema central. Aplicaciones y departamentos conectados dentro de un flujo de trabajo audiovisual completo.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

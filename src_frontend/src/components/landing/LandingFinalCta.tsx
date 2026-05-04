import { ArrowRight, ChevronRight } from 'lucide-react'
import LandingActionButton from '@/components/landing/LandingActionButton'
import LandingReveal from '@/components/landing/LandingReveal'

interface LandingFinalCtaProps {
  content: {
    eyebrow: string
    title: string
    description: string
    primaryCta: string
    secondaryCta: string
    bullets: readonly string[]
  }
  exploreCidTarget: string
  requestDemoTarget: string
}

export default function LandingFinalCta({
  content,
  exploreCidTarget,
  requestDemoTarget,
}: LandingFinalCtaProps) {
  return (
    <section id="cta-final" className="relative py-24">
      <div className="mx-auto max-w-6xl px-5 md:px-6 lg:px-8">
        <LandingReveal>
          <div className="landing-brand-final-cta rounded-[2.4rem] p-8 sm:p-10 lg:p-12">
            <div className="grid gap-10 lg:grid-cols-[1fr_auto] lg:items-end">
              <div>
                <p className="editorial-kicker text-amber-300">{content.eyebrow}</p>
                <h2 className="mt-4 max-w-4xl font-display text-4xl font-semibold leading-[0.92] text-white md:text-6xl">
                  {content.title}
                </h2>
                <p className="mt-5 max-w-3xl text-base leading-8 text-slate-200 md:text-lg">
                  {content.description}
                </p>
                <div className="mt-6 flex flex-wrap gap-3">
                  {content.bullets.map((bullet) => (
                    <span key={bullet} className="landing-pill">
                      {bullet}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row lg:flex-col">
                <LandingActionButton destination={requestDemoTarget} variant="primary">
                  {content.primaryCta}
                  <ArrowRight className="h-4 w-4" />
                </LandingActionButton>
                <LandingActionButton destination={exploreCidTarget} variant="secondary">
                  {content.secondaryCta}
                  <ChevronRight className="h-4 w-4" />
                </LandingActionButton>
                <LandingActionButton destination="/pricing" variant="ghost">
                  Ver precios
                </LandingActionButton>
              </div>
            </div>
          </div>
        </LandingReveal>
      </div>
    </section>
  )
}

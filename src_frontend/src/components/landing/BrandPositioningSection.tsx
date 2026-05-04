import type { LucideIcon } from 'lucide-react'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

interface BrandPositioningSectionProps {
  content: {
    eyebrow: string
    title: string
    description: string
    supportStrip: readonly string[]
    pillars: readonly {
      icon: LucideIcon
      title: string
      text: string
    }[]
  }
}

export default function BrandPositioningSection({ content }: BrandPositioningSectionProps) {
  return (
    <section id="que-es" className="relative py-24">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 md:px-6 lg:grid-cols-[0.96fr_1.04fr] lg:px-8">
        <LandingReveal>
          <LandingSectionHeading
            eyebrow={content.eyebrow}
            title={content.title}
            description={content.description}
          />
        </LandingReveal>

        <div className="grid gap-5 sm:grid-cols-3 lg:grid-cols-1">
          {content.pillars.map((pillar, index) => {
            const Icon = pillar.icon
            return (
              <LandingReveal key={pillar.title} delay={index * 110}>
                <div className="landing-panel rounded-[1.8rem] p-6">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-5 text-2xl font-semibold text-white">{pillar.title}</h3>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{pillar.text}</p>
                </div>
              </LandingReveal>
            )
          })}
        </div>

        <LandingReveal className="lg:col-span-2" delay={120}>
          <div className="grid gap-4 md:grid-cols-3">
            {content.supportStrip.map((item) => (
              <div key={item} className="rounded-[1.4rem] border border-white/10 bg-white/[0.04] px-5 py-5 text-sm leading-7 text-slate-200 backdrop-blur-xl">
                {item}
              </div>
            ))}
          </div>
        </LandingReveal>
      </div>
    </section>
  )
}

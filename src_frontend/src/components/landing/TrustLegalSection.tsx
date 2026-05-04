import type { LucideIcon } from 'lucide-react'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

interface TrustLegalSectionProps {
  content: {
    eyebrow: string
    title: string
    description: string
    items: readonly {
      icon: LucideIcon
      title: string
      text: string
    }[]
    notes: readonly string[]
  }
}

export default function TrustLegalSection({ content }: TrustLegalSectionProps) {
  return (
    <section id="legal" className="relative border-y border-white/10 bg-[#09111c]/82 py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
        <LandingReveal>
          <LandingSectionHeading
            eyebrow={content.eyebrow}
            title={content.title}
            description={content.description}
          />
        </LandingReveal>

        <div className="mt-14 grid gap-6 xl:grid-cols-[0.62fr_0.38fr]">
          <div className="grid gap-5 md:grid-cols-3 xl:grid-cols-1">
            {content.items.map((item, index) => {
              const Icon = item.icon
              return (
                <LandingReveal key={item.title} delay={index * 85}>
                  <div className="landing-panel rounded-[1.75rem] p-6">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h3 className="mt-5 text-2xl font-semibold text-white">{item.title}</h3>
                    <p className="mt-3 text-sm leading-7 text-slate-300">{item.text}</p>
                  </div>
                </LandingReveal>
              )
            })}
          </div>

          <LandingReveal delay={120}>
            <div className="landing-brand-trust-panel h-full rounded-[2rem] p-7">
              <p className="editorial-kicker text-amber-300">Principios de producto</p>
              <h3 className="mt-4 font-display text-4xl text-white">Software serio para una industria sensible a derechos, calidad y contexto.</h3>
              <div className="mt-8 space-y-4">
                {content.notes.map((note) => (
                  <div key={note} className="rounded-[1.2rem] border border-white/10 bg-white/[0.04] px-4 py-4 text-sm leading-7 text-slate-200">
                    {note}
                  </div>
                ))}
              </div>
            </div>
          </LandingReveal>
        </div>
      </div>
    </section>
  )
}

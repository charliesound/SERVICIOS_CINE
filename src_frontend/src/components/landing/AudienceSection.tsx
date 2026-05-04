import type { LucideIcon } from 'lucide-react'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

interface AudienceSectionProps {
  content: {
    eyebrow: string
    title: string
    description: string
    items: readonly {
      icon: LucideIcon
      title: string
      text: string
    }[]
  }
}

export default function AudienceSection({ content }: AudienceSectionProps) {
  return (
    <section id="para-quien" className="relative border-y border-white/10 bg-[#09111c]/70 py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
        <LandingReveal>
          <LandingSectionHeading
            eyebrow={content.eyebrow}
            title={content.title}
            description={content.description}
            align="center"
          />
        </LandingReveal>

        <div className="mt-14 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {content.items.map((item, index) => {
            const Icon = item.icon
            return (
              <LandingReveal key={item.title} delay={index * 90}>
                <div className="landing-panel h-full rounded-[1.8rem] p-6 text-center">
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-5 text-2xl font-semibold text-white">{item.title}</h3>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{item.text}</p>
                </div>
              </LandingReveal>
            )
          })}
        </div>
      </div>
    </section>
  )
}

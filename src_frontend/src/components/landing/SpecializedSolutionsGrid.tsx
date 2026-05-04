import type { LucideIcon } from 'lucide-react'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

interface SpecializedSolutionsGridProps {
  content: {
    eyebrow: string
    title: string
    description: string
    items: readonly {
      icon: LucideIcon
      title: string
      description: string
      tag: string
    }[]
  }
}

export default function SpecializedSolutionsGrid({ content }: SpecializedSolutionsGridProps) {
  return (
    <section id="soluciones" className="relative py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
        <LandingReveal>
          <LandingSectionHeading
            eyebrow={content.eyebrow}
            title={content.title}
            description={content.description}
          />
        </LandingReveal>

        <div className="mt-14 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {content.items.map((item, index) => {
            const Icon = item.icon
            return (
              <LandingReveal key={item.title} delay={index * 85}>
                <div className="landing-brand-solution-card h-full rounded-[1.85rem] p-6">
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-slate-400">
                      {item.tag}
                    </span>
                  </div>
                  <h3 className="mt-5 text-2xl font-semibold text-white">{item.title}</h3>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{item.description}</p>
                </div>
              </LandingReveal>
            )
          })}
        </div>
      </div>
    </section>
  )
}

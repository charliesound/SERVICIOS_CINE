import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

interface HowItWorksSectionProps {
  content: {
    eyebrow: string
    title: string
    description: string
    steps: readonly {
      step: string
      title: string
      text: string
    }[]
  }
}

export default function HowItWorksSection({ content }: HowItWorksSectionProps) {
  return (
    <section id="como-funciona" className="relative py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
        <LandingReveal>
          <LandingSectionHeading
            eyebrow={content.eyebrow}
            title={content.title}
            description={content.description}
            align="center"
          />
        </LandingReveal>

        <div className="mt-14 grid gap-5 lg:grid-cols-4">
          {content.steps.map((item, index) => (
            <LandingReveal key={item.step} delay={index * 80}>
              <div className="landing-brand-step-card h-full rounded-[1.8rem] p-6">
                <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-amber-300">{item.step}</p>
                <h3 className="mt-4 text-2xl font-semibold text-white">{item.title}</h3>
                <p className="mt-4 text-sm leading-7 text-slate-300">{item.text}</p>
              </div>
            </LandingReveal>
          ))}
        </div>
      </div>
    </section>
  )
}

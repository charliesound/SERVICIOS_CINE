import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

interface UseCasesSectionProps {
  content: {
    eyebrow: string
    title: string
    description: string
    items: readonly {
      title: string
      text: string
      outputs: readonly string[]
    }[]
  }
}

export default function UseCasesSection({ content }: UseCasesSectionProps) {
  return (
    <section id="casos" className="relative py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
        <LandingReveal>
          <LandingSectionHeading
            eyebrow={content.eyebrow}
            title={content.title}
            description={content.description}
          />
        </LandingReveal>

        <div className="mt-14 grid gap-5 md:grid-cols-2">
          {content.items.map((item, index) => (
            <LandingReveal key={item.title} delay={index * 85}>
              <div className="landing-panel h-full rounded-[1.9rem] p-6">
                <p className="text-[11px] uppercase tracking-[0.22em] text-cyan-200">Caso de uso</p>
                <h3 className="mt-4 text-3xl font-semibold text-white">{item.title}</h3>
                <p className="mt-4 text-sm leading-7 text-slate-300">{item.text}</p>
                <div className="mt-6 flex flex-wrap gap-2">
                  {item.outputs.map((output) => (
                    <span key={output} className="landing-pill text-slate-200">
                      {output}
                    </span>
                  ))}
                </div>
              </div>
            </LandingReveal>
          ))}
        </div>
      </div>
    </section>
  )
}

interface PricingModelBlockProps {
  title: string
  priceLines: readonly string[]
  description?: string
  bullets?: readonly string[]
  featured?: boolean
}

export default function PricingModelBlock({
  title,
  priceLines,
  description,
  bullets = [],
  featured = false,
}: PricingModelBlockProps) {
  return (
    <section className={`solution-pricing-block ${featured ? 'solution-pricing-block-featured' : ''}`}>
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="solution-eyebrow text-amber-300">Modelo comercial</p>
          <h2 className="mt-3 text-3xl font-semibold text-white">{title}</h2>
          {description ? <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">{description}</p> : null}
        </div>
        <div className="min-w-[240px] rounded-[1.4rem] border border-white/10 bg-white/[0.04] p-4">
          {priceLines.map((line) => (
            <p key={line} className="text-base font-medium text-white first:text-amber-200">
              {line}
            </p>
          ))}
        </div>
      </div>

      {bullets.length > 0 ? (
        <div className="mt-6 grid gap-3 md:grid-cols-3">
          {bullets.map((bullet) => (
            <div key={bullet} className="rounded-[1.25rem] border border-white/10 bg-white/[0.03] p-4 text-sm leading-7 text-slate-200">
              {bullet}
            </div>
          ))}
        </div>
      ) : null}
    </section>
  )
}

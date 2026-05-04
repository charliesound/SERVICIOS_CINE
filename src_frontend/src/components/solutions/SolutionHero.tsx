import { ArrowRight, ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'

interface SolutionHeroProps {
  eyebrow: string
  title: string
  description: string
  primaryLabel?: string
  primaryTo?: string
  secondaryLabel?: string
  secondaryTo?: string
  highlights?: readonly string[]
}

export default function SolutionHero({
  eyebrow,
  title,
  description,
  primaryLabel,
  primaryTo,
  secondaryLabel,
  secondaryTo,
  highlights = [],
}: SolutionHeroProps) {
  return (
    <section className="relative overflow-hidden pt-28 md:pt-36 lg:pt-40">
      <div className="landing-hero-radial" />
      <div className="mx-auto max-w-7xl px-5 pb-20 md:px-6 lg:px-8">
        <div className="solution-hero-panel">
          <div className="solution-grid-overlay" />
          <div className="relative z-10 max-w-4xl">
            <p className="editorial-kicker text-amber-300">{eyebrow}</p>
            <h1 className="mt-5 font-display text-5xl font-semibold leading-[0.9] tracking-[-0.04em] text-white sm:text-6xl md:text-7xl">
              {title}
            </h1>
            <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300 md:text-xl md:leading-9">
              {description}
            </p>

            {(primaryLabel && primaryTo) || (secondaryLabel && secondaryTo) ? (
              <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
                {primaryLabel && primaryTo ? (
                  <Link to={primaryTo} className="landing-cta-primary inline-flex">
                    {primaryLabel}
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                ) : null}
                {secondaryLabel && secondaryTo ? (
                  <Link to={secondaryTo} className="landing-cta-secondary inline-flex">
                    {secondaryLabel}
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                ) : null}
              </div>
            ) : null}

            {highlights.length > 0 ? (
              <div className="mt-8 flex flex-wrap gap-2.5">
                {highlights.map((highlight) => (
                  <span key={highlight} className="landing-pill">
                    {highlight}
                  </span>
                ))}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </section>
  )
}

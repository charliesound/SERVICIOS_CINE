import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { SolutionEntry } from '@/data/solutionsContent'

interface SolutionCardProps {
  solution: SolutionEntry
  featured?: boolean
}

export default function SolutionCard({ solution, featured = false }: SolutionCardProps) {
  const Icon = solution.icon

  return (
    <article className={`solution-card ${featured ? 'solution-card-featured' : ''}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
          <Icon className="h-5 w-5" />
        </div>
        <span className="solution-eyebrow rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-slate-300">
          {solution.type}
        </span>
      </div>

      <h3 className="mt-5 text-2xl font-semibold text-white">{solution.title}</h3>
      <p className="mt-2 text-sm font-medium text-amber-200">{solution.priceLabel}</p>
      <p className="mt-4 text-sm leading-7 text-slate-300">{solution.description}</p>

      <div className="mt-5 flex flex-wrap gap-2">
        {solution.bullets.map((bullet) => (
          <span key={bullet} className="landing-pill text-slate-200">
            {bullet}
          </span>
        ))}
      </div>

      <div className="mt-6">
        <Link to={solution.path} className="landing-cta-secondary inline-flex">
          {solution.ctaLabel}
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </article>
  )
}

import type { SolutionEntry } from '@/data/solutionsContent'
import SolutionCard from '@/components/solutions/SolutionCard'

interface SolutionGridProps {
  solutions: readonly SolutionEntry[]
}

export default function SolutionGrid({ solutions }: SolutionGridProps) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      {solutions.map((solution, index) => (
        <SolutionCard
          key={solution.slug}
          solution={solution}
          featured={solution.slug === 'cid' || index === 0}
        />
      ))}
    </div>
  )
}

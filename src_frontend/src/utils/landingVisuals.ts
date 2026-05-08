import { landingVisualBible, type LandingVisualRole, type LandingVisualSpec } from '@/data/landingVisualBible'

export function getLandingVisual(id: string): LandingVisualSpec {
  const visual = landingVisualBible.find((item) => item.id === id)

  if (!visual) {
    throw new Error(`Landing visual not found: ${id}`)
  }

  return visual
}

export function getLandingVisualsByRole(role: LandingVisualRole): LandingVisualSpec[] {
  return landingVisualBible.filter((item) => item.role === role)
}

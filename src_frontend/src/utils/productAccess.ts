import type { UserProfile } from '@/types'

export type ProductAccessUser = UserProfile | null

function hasPaidPlan(user: UserProfile): boolean {
  const plan = user.plan?.toLowerCase()
  return Boolean(plan && !['demo', 'free'].includes(plan))
}

function hasCidStudio(user: UserProfile): boolean {
  const program = user.program || user.plan?.toLowerCase()
  return program === 'studio' || program === 'enterprise'
}

export function getModuleAccessRoute(user: ProductAccessUser, moduleKey: string): string {
  const target = `/modules?module=${encodeURIComponent(moduleKey)}`
  if (!user) return `/login?next=${encodeURIComponent(target)}&product=${encodeURIComponent(moduleKey)}`
  if (hasCidStudio(user) || hasPaidPlan(user)) return target
  return `/pricing?product=${encodeURIComponent(moduleKey)}`
}

export function getModuleCheckoutRoute(moduleKey: string): string {
  return `/pricing?product=${encodeURIComponent(moduleKey)}`
}

export function getCidStudioPublicRoute(): string {
  return '/solutions/cid'
}

export function getCidStudioAccessRoute(user: ProductAccessUser): string {
  const target = '/cid/studio'
  if (!user) return getCidStudioPublicRoute()
  if (hasCidStudio(user)) return target
  return '/pricing?product=cidStudio'
}

export function getCidStudioCheckoutRoute(): string {
  return '/pricing?product=cidStudio'
}
